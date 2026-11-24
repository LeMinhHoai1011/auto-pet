from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, LargeBinary, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


# ── Pet Recognition Models ───────────────────────────────


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    breed: Mapped[str] = mapped_column(String(64), default="")
    color: Mapped[str] = mapped_column(String(64), default="")
    age_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    avatar_path: Mapped[str] = mapped_column(String(256), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_feed: Mapped[bool] = mapped_column(Boolean, default=True)
    portion_grams: Mapped[float] = mapped_column(Float, default=30.0)
    daily_limit_grams: Mapped[float] = mapped_column(Float, default=150.0)
    min_feed_interval_min: Mapped[int] = mapped_column(Integer, default=120)
    embedding_count: Mapped[int] = mapped_column(Integer, default=0)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_fed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, onupdate=datetime.utcnow)

    images: Mapped[list["PetImage"]] = relationship(back_populates="pet", cascade="all, delete-orphan")
    embeddings: Mapped[list["PetEmbedding"]] = relationship(back_populates="pet", cascade="all, delete-orphan")


class PetImage(Base):
    __tablename__ = "pet_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), index=True)
    image_path: Mapped[str] = mapped_column(String(256))
    source: Mapped[str] = mapped_column(String(32), default="upload")  # upload, camera, session
    is_face: Mapped[bool] = mapped_column(Boolean, default=False)
    phash: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)

    pet: Mapped["Pet"] = relationship(back_populates="images")


class PetEmbedding(Base):
    __tablename__ = "pet_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey("pets.id", ondelete="CASCADE"), index=True)
    image_id: Mapped[int | None] = mapped_column(ForeignKey("pet_images.id", ondelete="SET NULL"), nullable=True)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)  # numpy array serialized
    model_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)

    pet: Mapped["Pet"] = relationship(back_populates="embeddings")


class RecognitionSession(Base):
    __tablename__ = "recognition_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    tracker_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, assigned, rejected, stray
    suggested_pet_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_pet_id: Mapped[int | None] = mapped_column(ForeignKey("pets.id", ondelete="SET NULL"), nullable=True)
    similarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)

    samples: Mapped[list["RecognitionSample"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class RecognitionSample(Base):
    __tablename__ = "recognition_samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("recognition_sessions.id", ondelete="CASCADE"), index=True)
    image_path: Mapped[str] = mapped_column(String(256))
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    phash: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW)

    session: Mapped["RecognitionSession"] = relationship(back_populates="samples")


class RecognitionLog(Base):
    __tablename__ = "recognition_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    pet_id: Mapped[int | None] = mapped_column(ForeignKey("pets.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32))  # KNOWN, UNKNOWN, UNCERTAIN, etc.
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
    tracker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    image_path: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=_NOW, index=True)
