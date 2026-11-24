import asyncio
import json
import logging
import sys

import aiomqtt

from ..config import settings

logger = logging.getLogger("mqtt_pub")

TOPIC_PREFIX = f"petfeeder/{settings.device_id}/"


async def publish_command(command: str, payload: dict | None = None):
    topic = f"{TOPIC_PREFIX}command"
    data = {"cmd": command}
    if payload:
        data.update(payload)

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _publish_sync, topic, data)
        return result
    except Exception as e:
        logger.warning("Publish failed: %s", e)
        return False


def _publish_sync(topic: str, data: dict) -> bool:
    import paho.mqtt.publish as publish
    try:
        auth = None
        if settings.mqtt_user:
            auth = {"username": settings.mqtt_user, "password": settings.mqtt_pass}
        publish.single(
            topic,
            payload=json.dumps(data),
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            auth=auth,
        )
        logger.info("Published %s → %s", topic, data)
        return True
    except Exception as e:
        logger.warning("Publish failed: %s", e)
        return False
