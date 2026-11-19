from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://petfeeder:changeme123@db:5432/petfeeder"

    mqtt_host: str = "mosquitto"
    mqtt_port: int = 1883
    mqtt_user: str = "mqtt_user"
    mqtt_pass: str = "mqtt_pass"

    fcm_credentials_path: str = "/app/firebase-credentials.json"

    secret_key: str = "change-this"
    device_id: str = "device01"

    model_config = {"env_file": ".env"}


settings = Settings()
