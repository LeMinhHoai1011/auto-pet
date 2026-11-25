from datetime import datetime
from pydantic import BaseModel, Field


class FeedRequest(BaseModel):
    grams: float = Field(30.0, ge=1, le=150, allow_inf_nan=False)


class ScheduleCreate(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    grams: float = Field(30.0, ge=1, le=150, allow_inf_nan=False)
    enabled: bool = True
    pet_id: int | None = Field(None, gt=0)


class ScheduleUpdate(BaseModel):
    hour: int | None = Field(None, ge=0, le=23)
    minute: int | None = Field(None, ge=0, le=59)
    grams: float | None = Field(None, ge=1, le=150, allow_inf_nan=False)
    enabled: bool | None = None


class ScheduleOut(BaseModel):
    id: int
    hour: int
    minute: int
    grams: float
    enabled: bool
    pet_id: int | None = None
    model_config = {"from_attributes": True}


class PetMealOut(BaseModel):
    id: str
    pet_id: int
    scheduled_at: datetime
    dispensed_at: datetime | None
    eaten_at: datetime | None
    grams: float
    status: str
    model_config = {"from_attributes": True}


class FeedingOut(BaseModel):
    id: int
    source: str
    result: str
    actual_grams: float
    created_at: datetime
    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    alert_type: str
    message: str
    resolved: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class DeviceStateOut(BaseModel):
    bowl_grams: float
    hopper_pct: int
    temperature: float
    humidity: float
    stale_score: float
    online: bool
    last_feed_at: datetime | None
    updated_at: datetime
    model_config = {"from_attributes": True}


class SensorOut(BaseModel):
    sensor_type: str
    value: float
    unit: str
    created_at: datetime
    model_config = {"from_attributes": True}


class FCMTokenRegister(BaseModel):
    token: str
    device_name: str = ""


# ── Pet Recognition Schemas ──────────────────────────────


class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    breed: str = ""
    color: str = ""
    age_months: int | None = None
    weight_kg: float | None = None
    notes: str = ""
    portion_grams: float = Field(30.0, ge=1, le=150)
    daily_limit_grams: float = Field(150.0, ge=1, le=500)
    min_feed_interval_min: int = Field(120, ge=0, le=1440)
    auto_feed: bool = True


class PetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    breed: str | None = None
    color: str | None = None
    age_months: int | None = None
    weight_kg: float | None = None
    notes: str | None = None
    portion_grams: float | None = Field(None, ge=1, le=150)
    daily_limit_grams: float | None = Field(None, ge=1, le=500)
    min_feed_interval_min: int | None = Field(None, ge=0, le=1440)
    auto_feed: bool | None = None
    active: bool | None = None


class PetOut(BaseModel):
    id: int
    name: str
    breed: str
    color: str
    age_months: int | None
    weight_kg: float | None
    notes: str
    avatar_path: str
    active: bool
    auto_feed: bool
    portion_grams: float
    daily_limit_grams: float
    min_feed_interval_min: int
    embedding_count: int
    last_seen_at: datetime | None
    last_fed_at: datetime | None
    created_at: datetime
    model_config = {"from_attributes": True}


class PetImageOut(BaseModel):
    id: int
    pet_id: int
    image_path: str
    source: str
    is_face: bool
    confirmed: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class RecognitionSessionOut(BaseModel):
    id: int
    session_id: str
    tracker_id: int
    status: str
    suggested_pet_id: int | None
    assigned_pet_id: int | None
    similarity_score: float
    image_count: int
    started_at: datetime
    ended_at: datetime | None
    model_config = {"from_attributes": True}


class RecognitionLogOut(BaseModel):
    id: int
    pet_id: int | None
    status: str
    similarity: float
    tracker_id: int | None
    session_id: str | None
    image_path: str
    created_at: datetime
    model_config = {"from_attributes": True}


class SessionAssign(BaseModel):
    pet_id: int | None = None
    create_new: bool = False
    new_pet_name: str = ""
    selected_sample_ids: list[int] = []


class PipelineStatusOut(BaseModel):
    mode: str
    camera_state: str
    fps: float
    ai_fps: float
    process_time_ms: float
    cats_detected: int
    active_sessions: int
    total_collected: int
    device_info: str
    error: str
