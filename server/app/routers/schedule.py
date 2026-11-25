from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models import Pet, PetMeal, Schedule, SchedulePet
from ..schemas import PetMealOut, ScheduleCreate, ScheduleUpdate, ScheduleOut
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
    if req.pet_id is None and sum(row.pet_id is None for row in existing) >= 6:
        raise HTTPException(422, "Device supports at most 6 schedules")
    if req.pet_id is not None:
        pet = await db.get(Pet, req.pet_id)
        if pet is None or not pet.active or not pet.embedding_count:
            raise HTTPException(422, "Thú cưng cần có mẫu nhận diện")
    sched = Schedule(
        device_id=settings.device_id,
        hour=req.hour, minute=req.minute,
        grams=req.grams, enabled=req.enabled,
    )
    sched.assignment = (
        SchedulePet(pet_id=req.pet_id, key=uuid4().hex) if req.pet_id is not None else None
    )
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    if req.pet_id is None:
        await _sync_schedules_to_device(db)
    return sched


@router.get("/pet-meals", response_model=list[PetMealOut])
async def list_pet_meals(db: AsyncSession = Depends(get_db)):
    return (await db.scalars(
        select(PetMeal).where(PetMeal.device_id == settings.device_id)
        .order_by(PetMeal.scheduled_at.desc()).limit(100)
    )).all()


@router.patch("/{schedule_id}", response_model=ScheduleOut)
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
    if sched.pet_id is None:
        await _sync_schedules_to_device(db)
    return sched


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Schedule).where(
        Schedule.id == schedule_id, Schedule.device_id == settings.device_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(404, "Schedule not found")
    device_schedule = sched.pet_id is None
    await db.delete(sched)
    await db.commit()
    if device_schedule:
        await _sync_schedules_to_device(db)
    return {"ok": True}


async def _sync_schedules_to_device(db: AsyncSession):
    result = await db.execute(
        select(Schedule)
        .where(Schedule.device_id == settings.device_id, Schedule.enabled == True)
        .order_by(Schedule.hour, Schedule.minute)
    )
    meals = [{"h": s.hour, "m": s.minute, "g": s.grams}
             for s in result.scalars().all() if s.pet_id is None]
    await publish_command("SCHEDULE", {"meals": meals})
