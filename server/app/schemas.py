from datetime import datetime
from pydantic import BaseModel, Field


class FeedRequest(BaseModel):
    grams: float = Field(30.0, ge=1, le=150, allow_inf_nan=False)


class ScheduleCreate(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    grams: float = Field(30.0, ge=1, le=150, allow_inf_nan=False)
    enabled: bool = True


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
