from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models import SensorLog
from ..schemas import SensorOut

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("/", response_model=list[SensorOut])
async def list_sensors(
    sensor_type: str = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SensorLog).where(SensorLog.device_id == settings.device_id)
    if sensor_type:
        stmt = stmt.where(SensorLog.sensor_type == sensor_type)
    stmt = stmt.order_by(SensorLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
