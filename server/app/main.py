import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import device, feed, schedule, alerts, sensors, push
from .services.mqtt_service import mqtt_listener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


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
