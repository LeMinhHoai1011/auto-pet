from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models import Schedule
from ..schemas import ScheduleCreate, ScheduleUpdate, ScheduleOut
from ..services.mqtt_publisher import publish_command

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/", response_model=list[ScheduleOut])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Schedule)
        .where(Schedule.device_id == settings.device_id)
        .order_by(Schedule.hour, Schedule.minute)
    )
    return result.scalars().all()


@router.post("/", response_model=ScheduleOut)
async def create_schedule(req: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    existing = await list_schedules(db)
    if len(existing) >= 6:
        raise HTTPException(422, "Device supports at most 6 schedules")
    sched = Schedule(
        device_id=settings.device_id,
        hour=req.hour, minute=req.minute,
        grams=req.grams, enabled=req.enabled,
    )
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    await _sync_schedules_to_device(db)
    return sched


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int, req: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Schedule).where(
        Schedule.id == schedule_id, Schedule.device_id == settings.device_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(404, "Schedule not found")
    if req.hour is not None:
        sched.hour = req.hour
    if req.minute is not None:
        sched.minute = req.minute
    if req.grams is not None:
        sched.grams = req.grams
    if req.enabled is not None:
        sched.enabled = req.enabled
    await db.commit()
    await db.refresh(sched)
    await _sync_schedules_to_device(db)
    return sched


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Schedule).where(
        Schedule.id == schedule_id, Schedule.device_id == settings.device_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(404, "Schedule not found")
    await db.delete(sched)
    await db.commit()
    await _sync_schedules_to_device(db)
    return {"ok": True}


async def _sync_schedules_to_device(db: AsyncSession):
    result = await db.execute(
        select(Schedule)
        .where(Schedule.device_id == settings.device_id, Schedule.enabled == True)
        .order_by(Schedule.hour, Schedule.minute)
    )
    meals = [{"h": s.hour, "m": s.minute, "g": s.grams}
             for s in result.scalars().all()]
    await publish_command("SCHEDULE", {"meals": meals})
