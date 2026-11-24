import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .routers import device, feed, schedule, alerts, sensors, push
from .services.mqtt_service import mqtt_listener
from .services.ws_manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(mqtt_listener())
    logging.getLogger("app").info("Server started — MQTT listener running")
    yield
    task.cancel()


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


@app.get("/")
async def dashboard_index():
    return FileResponse(DASHBOARD_DIR / "index.html", media_type="text/html")


app.mount("/", StaticFiles(directory=str(DASHBOARD_DIR)), name="dashboard")
