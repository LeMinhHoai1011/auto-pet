import json
import logging

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
        async with aiomqtt.Client(
            hostname=settings.mqtt_host,
            port=settings.mqtt_port,
            username=settings.mqtt_user,
            password=settings.mqtt_pass,
        ) as client:
            await client.publish(topic, json.dumps(data))
            logger.info("Published %s → %s", topic, data)
            return True
    except Exception as e:
        logger.warning("Publish failed: %s", e)
        return False
