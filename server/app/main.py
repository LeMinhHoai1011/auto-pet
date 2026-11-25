import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from .database import init_db
from .routers import device, feed, schedule, alerts, sensors, push, pets, recognition
from .services.mqtt_service import mqtt_listener
from .services.pet_meals import monitor_pet_meals
from .services.ws_manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"

from .recognition import torch_available, torch_error

RECOGNITION_BLOCKED = torch_error or "Windows Application Control blocked a recognition dependency."


def _is_application_control_error(exc: OSError) -> bool:
    return getattr(exc, "winerror", None) == 4551


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    pipeline = None
    if torch_available:
        await _load_embedding_store()
        try:
            from .recognition.pipeline import pipeline
        except OSError as exc:
            if not _is_application_control_error(exc):
                raise
            logging.getLogger("app").warning("%s %s", RECOGNITION_BLOCKED, exc)
    else:
        logging.getLogger("app").warning(
            "AI recognition disabled: %s", RECOGNITION_BLOCKED
        )
    task = asyncio.create_task(mqtt_listener())
    meal_task = asyncio.create_task(monitor_pet_meals(pipeline))
    logging.getLogger("app").info("Server started — MQTT listener running")
    try:
        yield
    finally:
        task.cancel()
        meal_task.cancel()
        await asyncio.gather(meal_task, return_exceptions=True)
        if pipeline is not None:
            try:
                pipeline.stop()
                from .recognition.detector import unload_model as unload_yolo
                from .recognition.embedding import unload_model as unload_emb
                unload_yolo()
                unload_emb()
            except Exception:
                logging.getLogger("app").exception("Failed to clean up recognition resources")


app = FastAPI(
    title="Pet Feeder API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(OSError)
async def handle_application_control_error(request: Request, exc: OSError):
    if not _is_application_control_error(exc):
        raise exc
    return JSONResponse(status_code=503, content={"detail": RECOGNITION_BLOCKED})

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
    return {
        "status": "ok",
        "service": "pet-feeder-api",
        "ai_available": torch_available,
        "ai_error": torch_error or None,
    }


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
