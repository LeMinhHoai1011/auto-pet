from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import DeviceState
from ..schemas import DeviceStateOut

router = APIRouter(prefix="/api/device", tags=["device"])


@router.get("/status", response_model=DeviceStateOut | None)
async def get_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DeviceState).where(DeviceState.device_id == settings.device_id)
    )
    return result.scalar_one_or_none()
