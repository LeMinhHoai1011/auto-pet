from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

_NOW = text("CURRENT_TIMESTAMP")


class FeedingLog(Base):
    __tablename__ = "feeding_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(16))
    result: Mapped[str] = mapped_column(String(16), default="ok")
    target_grams: Mapped[float] = mapped_column(Float, default=0)
    actual_grams: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, index=True)


class SensorLog(Base):
    __tablename__ = "sensor_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(32), index=True)
    sensor_type: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(16), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, index=True)


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(32), index=True)
    alert_type: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(Text, default="")
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, index=True)


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(32), index=True)
    hour: Mapped[int] = mapped_column(Integer)
    minute: Mapped[int] = mapped_column(Integer)
    grams: Mapped[float] = mapped_column(Float, default=30.0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)


class DeviceState(Base):
    __tablename__ = "device_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[str] = mapped_column(String(32), unique=True)
    bowl_grams: Mapped[float] = mapped_column(Float, default=0)
    hopper_pct: Mapped[int] = mapped_column(Integer, default=100)
    temperature: Mapped[float] = mapped_column(Float, default=25)
    humidity: Mapped[float] = mapped_column(Float, default=50)
    wifi_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    mqtt_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    stale_score: Mapped[float] = mapped_column(Float, default=0)
    last_feed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    online: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, onupdate=datetime.utcnow)


class FCMToken(Base):
    __tablename__ = "fcm_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(256), unique=True)
    device_name: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)
