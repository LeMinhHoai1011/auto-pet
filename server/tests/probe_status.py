"""Request telemetry without actuating the motor or modifying the scale."""
import asyncio
import httpx
from app.services.mqtt_publisher import publish_command


async def main():
    print("STATUS published:", await publish_command("STATUS"))
    await asyncio.sleep(3)
    async with httpx.AsyncClient(base_url="http://nginx") as client:
        print("Device state:", (await client.get("/api/device/status")).text)


if __name__ == "__main__":
    asyncio.run(main())
