import asyncio
import json
import logging
import sys
import threading

import aiomqtt

from ..config import settings
from ..database import async_session
from ..models import FeedingLog, SensorLog, AlertLog, DeviceState
from .pet_meals import record_dispense
from .push_service import send_push
from .ws_manager import ws_manager

logger = logging.getLogger("mqtt")

TOPIC_PREFIX = f"petfeeder/{settings.device_id}/"

SUBSCRIBE_TOPICS = [
    f"{TOPIC_PREFIX}status",
    f"{TOPIC_PREFIX}event",
    f"{TOPIC_PREFIX}sensor/weight",
    f"{TOPIC_PREFIX}sensor/food_level",
    f"{TOPIC_PREFIX}sensor/env",
    f"{TOPIC_PREFIX}feeding",
    f"{TOPIC_PREFIX}alert",
    f"{TOPIC_PREFIX}vision/pet_detected",
]

_main_loop: asyncio.AbstractEventLoop | None = None


async def _upsert_device_state(session, device_id: str, **kwargs):
    from sqlalchemy import select
    stmt = select(DeviceState).where(DeviceState.device_id == device_id)
    result = await session.execute(stmt)
    state = result.scalar_one_or_none()
    if state is None:
        state = DeviceState(device_id=device_id, **kwargs)
        session.add(state)
    else:
        for k, v in kwargs.items():
            setattr(state, k, v)
    await session.commit()


async def _handle_message(topic: str, payload: str):
    device_id = settings.device_id
    suffix = topic.removeprefix(TOPIC_PREFIX)
    if suffix == "status" and payload in ("online", "offline"):
        async with async_session() as session:
            await _upsert_device_state(session, device_id, online=payload == "online")
        return
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON on %s: %s", topic, payload)
        return
    if not isinstance(data, dict):
        logger.warning("Expected JSON object on %s", topic)
        return

    device_id = settings.device_id
    suffix = topic.replace(TOPIC_PREFIX, "")

    async with async_session() as session:
        if suffix == "sensor/weight":
            val = data.get("bowl_g", data.get("g", data.get("value", 0)))
            session.add(SensorLog(device_id=device_id, sensor_type="weight", value=val, unit="g"))
            await _upsert_device_state(session, device_id, bowl_grams=val)

        elif suffix == "sensor/food_level":
            pct = data.get("hopper_pct", data.get("pct", data.get("value", 0)))
            session.add(SensorLog(device_id=device_id, sensor_type="food_level", value=pct, unit="%"))
            await _upsert_device_state(session, device_id, hopper_pct=int(pct))

        elif suffix == "sensor/env":
            temp = data.get("temp", data.get("temperature", 25))
            hum = data.get("hum", data.get("humidity", 50))
            session.add(SensorLog(device_id=device_id, sensor_type="temperature", value=temp, unit="C"))
            session.add(SensorLog(device_id=device_id, sensor_type="humidity", value=hum, unit="%"))
            await _upsert_device_state(session, device_id, temperature=temp, humidity=hum)

        elif suffix == "feeding":
            src = data.get("src", "unknown")
            result = data.get("result", "ok")
            actual = data.get("actual_g", 0)
            from datetime import datetime
            session.add(FeedingLog(
                device_id=device_id, source=src, result=result,
                actual_grams=actual,
            ))
            await _upsert_device_state(session, device_id, last_feed_at=datetime.utcnow())
            await send_push(
                f"Cho an: {actual:.0f}g",
                f"Nguon: {src} | Ket qua: {result}",
            )

        elif suffix == "event":
            event_type = data.get("type", "unknown")
            if event_type == "pet_feed_result":
                await record_dispense(session, data)
            elif event_type in ("fed", "skipped"):
                src = data.get("src", "unknown")
                grams = data.get("g", 0)
                session.add(FeedingLog(
                    device_id=device_id, source=src, result=event_type,
                    actual_grams=grams,
                ))

        elif suffix == "alert":
            alert_type = data.get("type", "unknown")
            msg = data.get("msg", data.get("message", ""))
            session.add(AlertLog(device_id=device_id, alert_type=alert_type, message=msg))
            await send_push(f"Canh bao: {alert_type}", msg)

        elif suffix == "status":
            bowl = data.get("bowl_g", 0)
            hopper = data.get("hopper_pct", 0)
            await _upsert_device_state(session, device_id,
                bowl_grams=bowl, hopper_pct=hopper, online=True)

        elif suffix == "vision/pet_detected":
            pet = data.get("pet", "unknown")
            conf = data.get("confidence", 0)
            session.add(SensorLog(
                device_id=device_id, sensor_type="vision",
                value=conf, unit=pet,
            ))

        await session.commit()

    _schedule_ws_broadcast(suffix, payload)
    logger.info("Processed %s: %s", suffix, payload[:120])


def _schedule_ws_broadcast(suffix: str, payload: str):
    if _main_loop is not None and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(_ws_broadcast(suffix, payload), _main_loop)


async def _ws_broadcast(suffix: str, payload: str):
    try:
        data = {"topic": suffix}
        try:
            data["data"] = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            data["data"] = payload
        await ws_manager.broadcast(data)
    except Exception:
        pass


def _mqtt_thread_target():
    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_mqtt_loop())


async def _mqtt_loop():
    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_host,
                port=settings.mqtt_port,
                username=settings.mqtt_user,
                password=settings.mqtt_pass,
            ) as client:
                for t in SUBSCRIBE_TOPICS:
                    await client.subscribe(t)
                logger.info("MQTT connected, subscribed to %d topics", len(SUBSCRIBE_TOPICS))

                async for msg in client.messages:
                    topic = str(msg.topic)
                    payload = msg.payload.decode() if msg.payload else ""
                    await _handle_message(topic, payload)

        except aiomqtt.MqttError as e:
            logger.warning("MQTT disconnected: %s — reconnecting in 5s", e)
            await asyncio.sleep(5)
        except Exception as e:
            logger.exception("MQTT error: %s", e)
            await asyncio.sleep(5)


async def mqtt_listener():
    global _main_loop
    _main_loop = asyncio.get_running_loop()
    thread = threading.Thread(target=_mqtt_thread_target, daemon=True)
    thread.start()
    logger.info("MQTT listener thread started")
    while thread.is_alive():
        await asyncio.sleep(1)
