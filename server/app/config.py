import os
from pathlib import Path

from pydantic_settings import BaseSettings

_server_dir = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str = f"sqlite+aiosqlite:///{_server_dir / 'petfeeder.db'}"

    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_user: str = "mqtt_user"
    mqtt_pass: str = "mqtt_pass"

    fcm_credentials_path: str = str(_server_dir / "firebase-credentials.json")

    secret_key: str = "change-this"
    device_id: str = "device01"

    model_config = {"env_file": str(_server_dir / ".env")}


settings = Settings()
