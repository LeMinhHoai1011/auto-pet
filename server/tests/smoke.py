"""Read-only HTTP checks and MQTT echo on a dedicated non-device topic."""
import asyncio
import uuid
import httpx
import aiomqtt
from app.config import settings


async def main():
    async with httpx.AsyncClient(base_url="http://nginx", timeout=10) as client:
        for path in ("/", "/docs", "/openapi.json", "/api/health",
                     "/api/device/status", "/api/schedule/", "/api/feed/history",
                     "/api/alerts/", "/api/sensors/"):
            response = await client.get(path)
            response.raise_for_status()
            print(f"HTTP {response.status_code}: {path}")
    async with aiomqtt.Client(hostname=settings.mqtt_host, port=settings.mqtt_port,
                             username=settings.mqtt_user, password=settings.mqtt_pass) as client:
        topic = f"petfeeder/__smoke__/{uuid.uuid4().hex}"
        await client.subscribe(topic)
        await client.publish(topic, "ping")
        async with asyncio.timeout(5):
            async for message in client.messages:
                assert str(message.topic) == topic and message.payload == b"ping"
                print("MQTT authenticated publish/subscribe: OK")
                break


asyncio.run(main())
