import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from .database import init_db
from .routers import device, feed, schedule, alerts, sensors, push, pets, recognition
from .services.mqtt_service import mqtt_listener
from .services.ws_manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"


async def _load_embedding_store():
    """Load registered pet embeddings into memory on startup."""
    import numpy as np
    from .database import async_session
    from .models import Pet, PetEmbedding
    from .recognition.matcher import embedding_store
    from sqlalchemy import select

    try:
        async with async_session() as session:
            result = await session.execute(select(Pet).where(Pet.active == True))
            pets_list = result.scalars().all()
            for pet in pets_list:
                emb_result = await session.execute(
                    select(PetEmbedding).where(PetEmbedding.pet_id == pet.id)
                )
                embeddings = []
                for emb in emb_result.scalars().all():
                    arr = np.frombuffer(emb.embedding, dtype=np.float32)
                    embeddings.append(arr)
                if embeddings:
                    embedding_store.update_pet(pet.id, pet.name, embeddings)
        logging.getLogger("app").info(
            "Embedding store loaded: %d pets", embedding_store.pet_count
        )
    except Exception:
        logging.getLogger("app").exception("Failed to load embedding store")


def _setup_auto_feed():
    """Register callback: when AI confirms a pet, auto-feed its portion."""
    import asyncio
    from .recognition.pipeline import pipeline
    from .database import async_session
    from .models import Pet, FeedingLog
    from .services.mqtt_publisher import publish_command
    from sqlalchemy import select, func
    from datetime import datetime, timedelta

    _logger = logging.getLogger("auto_feed")
    _main_loop = asyncio.get_event_loop()

    def on_pet_confirmed(pet_id: int, pet_name: str, tracker_id: int):
        asyncio.run_coroutine_threadsafe(
            _do_auto_feed(pet_id, pet_name, tracker_id), _main_loop
        )

    async def _do_auto_feed(pet_id: int, pet_name: str, tracker_id: int):
        try:
            async with async_session() as session:
                result = await session.execute(select(Pet).where(Pet.id == pet_id))
                pet = result.scalar_one_or_none()
                if not pet or not pet.auto_feed:
                    _logger.info("Pet %s: auto_feed disabled, skipping", pet_name)
                    return

                now = datetime.utcnow()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                fed_today = await session.execute(
                    select(func.coalesce(func.sum(FeedingLog.actual_grams), 0))
                    .where(FeedingLog.created_at >= today_start)
                    .where(FeedingLog.source == f"ai_pet_{pet_id}")
                )
                total_today = fed_today.scalar() or 0

                if total_today + pet.portion_grams > pet.daily_limit_grams:
                    _logger.info("Pet %s: daily limit %.0fg reached (fed %.0fg), skipping",
                                 pet_name, pet.daily_limit_grams, total_today)
                    return

                recent = await session.execute(
                    select(FeedingLog)
                    .where(FeedingLog.source == f"ai_pet_{pet_id}")
                    .where(FeedingLog.created_at >= now - timedelta(minutes=pet.min_feed_interval_min))
                    .limit(1)
                )
                if recent.scalar_one_or_none():
                    _logger.info("Pet %s: fed within last %d min, skipping",
                                 pet_name, pet.min_feed_interval_min)
                    return

            _logger.info("Auto-feed: %s → %.0fg", pet_name, pet.portion_grams)
            await publish_command("FEED", {"g": pet.portion_grams})

            async with async_session() as session:
                session.add(FeedingLog(
                    device_id=settings.device_id,
                    source=f"ai_pet_{pet_id}",
                    result="SENT",
                    actual_grams=pet.portion_grams,
                ))
                await session.commit()

            await ws_manager.broadcast({
                "topic": "auto_feed",
                "data": {"pet_id": pet_id, "pet_name": pet_name, "grams": pet.portion_grams},
            })

        except Exception:
            _logger.exception("Auto-feed error for pet %s", pet_name)

    pipeline.set_on_pet_confirmed(on_pet_confirmed)
    _logger.info("Auto-feed callback registered")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _load_embedding_store()
    _setup_auto_feed()
    task = asyncio.create_task(mqtt_listener())
    logging.getLogger("app").info("Server started — MQTT listener running")
    yield
    task.cancel()
    # Cleanup recognition resources
    try:
        from .recognition.pipeline import pipeline
        pipeline.stop()
        from .recognition.detector import unload_model as unload_yolo
        from .recognition.embedding import unload_model as unload_emb
        unload_yolo()
        unload_emb()
    except Exception:
        pass


app = FastAPI(
    title="Pet Feeder API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(device.router)
app.include_router(feed.router)
app.include_router(schedule.router)
app.include_router(alerts.router)
app.include_router(sensors.router)
app.include_router(push.router)
app.include_router(pets.router)
app.include_router(recognition.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "pet-feeder-api"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(ws)


@app.get("/pet-demo")
async def pet_demo_page():
    return FileResponse(DASHBOARD_DIR / "pet-demo.html", media_type="text/html")


@app.get("/ai")
async def ai_dashboard_page():
    return RedirectResponse("/#/ai")


@app.get("/")
async def dashboard_index():
    return FileResponse(DASHBOARD_DIR / "index.html", media_type="text/html")


# Serve stored images (pet photos, pending session photos)
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

app.mount("/", StaticFiles(directory=str(DASHBOARD_DIR)), name="dashboard")
