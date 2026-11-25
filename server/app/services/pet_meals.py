import asyncio
import hashlib
import logging
import math
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from ..config import settings
from ..database import async_session
from ..models import AlertLog, Pet, PetMeal, Schedule, SchedulePet, SensorLog
from .mqtt_publisher import publish_command
from .push_service import send_push
from .ws_manager import ws_manager

logger = logging.getLogger(__name__)
LOCAL_TIME = timezone(timedelta(hours=7))
MEAL_WINDOW = timedelta(minutes=30)
WEIGHT_MAX_AGE = timedelta(seconds=12)
DISPENSE_WAIT = timedelta(seconds=60)
_meal_check_lock = asyncio.Lock()
NO_OPEN_MEAL = "Thú cưng chưa có cữ ăn đang mở. Mỗi cữ có hiệu lực trong 30 phút từ giờ đã đặt."


def _epoch(utc: datetime) -> float:
    return utc.replace(tzinfo=timezone.utc).timestamp()


async def record_dispense(session, data):
    request_id = data.get("id")
    grams = data.get("actual_g")
    if not isinstance(request_id, str) or not isinstance(grams, (float, int)):
        return
    if not math.isfinite(grams) or grams < 0:
        return
    meal = await session.get(PetMeal, request_id)
    if meal is None or meal.device_id != settings.device_id or meal.status != "requested":
        return
    if grams > 0:
        meal.dispensed_at = datetime.utcnow()
        meal.status = "dispensed"
        meal.grams = grams
    else:
        meal.status = "failed"
        meal.grams = 0


def _eating_evidence(samples, meal, presence):
    if not presence or presence[0] != meal.pet_id or len(samples) < 3:
        return False
    _, seen_since, last_seen = presence
    newest, previous = samples[:2]
    if not meal.dispensed_at or _epoch(newest.created_at) > last_seen:
        return False
    for baseline in samples[2:]:
        if baseline.created_at <= meal.dispensed_at or _epoch(baseline.created_at) < seen_since:
            break
        if baseline.value >= max(3, meal.grams * 0.75):
            if (baseline.value - max(newest.value, previous.value) >= 3
                    and abs(newest.value - previous.value) <= 2):
                return True
    return False


def _expire(session, meal, pet, local_due):
    clock = local_due.strftime("%H:%M")
    if meal.status == "dispensed":
        message = f"Chưa xác nhận {pet.name} đã ăn cữ {clock}."
        meal.status = "unconfirmed"
    elif meal.status == "requested":
        message = f"Chưa xác nhận máy đã nhả cho {pet.name} cữ {clock}."
        meal.status = "unconfirmed"
    else:
        message = f"{pet.name} chưa ăn cữ {clock}."
        meal.status = "missed"
    alert_type = "pet_meal_missed" if meal.status == "missed" else "pet_meal_unconfirmed"
    session.add(AlertLog(device_id=settings.device_id, alert_type=alert_type, message=message))
    return alert_type, message


async def request_photo_feed(pet_id: int) -> tuple[str | None, str]:
    async with _meal_check_lock:
        return await _check_meals(None, photo_pet_id=pet_id)


async def _check_meals(pipeline, *, photo_pet_id: int | None = None) -> tuple[str | None, str]:
    now = datetime.utcnow()
    local_now = now.replace(tzinfo=timezone.utc).astimezone(LOCAL_TIME)
    presence = pipeline.feeding_presence() if pipeline is not None else None
    if presence and time.time() - presence[2] > 3:
        presence = None
    async with async_session() as session:
        query = (
            select(Schedule, SchedulePet, Pet)
            .join(SchedulePet, SchedulePet.schedule_id == Schedule.id)
            .join(Pet, Pet.id == SchedulePet.pet_id)
            .where(Schedule.device_id == settings.device_id, Schedule.enabled, Pet.active)
            .order_by(Schedule.hour, Schedule.minute, Schedule.id)
        )
        if photo_pet_id is not None:
            query = query.where(Pet.id == photo_pet_id)
        schedules = (await session.execute(query)).all()
        if not schedules:
            return None, "Thú cưng chưa có lịch riêng đang bật."
        blocked_reason = NO_OPEN_MEAL
        samples = (await session.scalars(
            select(SensorLog).where(
                SensorLog.device_id == settings.device_id,
                SensorLog.sensor_type == "weight",
                SensorLog.created_at >= now - timedelta(minutes=5),
            ).order_by(SensorLog.created_at.desc(), SensorLog.id.desc()).limit(64)
        )).all()
        latest = samples[0] if samples else None
        device_busy = await session.scalar(select(PetMeal.id).where(
            PetMeal.device_id == settings.device_id,
            PetMeal.requested_at >= now - DISPENSE_WAIT,
        ).limit(1))
        for schedule, assignment, pet in schedules:
            local_due = local_now.replace(
                hour=schedule.hour, minute=schedule.minute, second=0, microsecond=0
            )
            if local_due > local_now:
                local_due -= timedelta(days=1)
            due = local_due.astimezone(timezone.utc).replace(tzinfo=None)
            deadline = due + MEAL_WINDOW
            if schedule.created_at >= deadline:
                continue
            request_id = hashlib.sha256(f"{assignment.key}:{due.isoformat()}".encode()).hexdigest()[:32]
            meal = await session.get(PetMeal, request_id)
            if photo_pet_id is not None and now < deadline and meal is not None:
                blocked_reason = "Cữ này đã có yêu cầu nhả hoặc đã được xử lý."
            if meal and meal.status in ("eaten", "missed", "unconfirmed"):
                continue
            if meal and meal.status == "dispensed" and latest:
                if now - latest.created_at <= WEIGHT_MAX_AGE and _eating_evidence(samples, meal, presence):
                    meal.status = "eaten"
                    meal.eaten_at = now
                    await session.commit()
                    continue
            if meal and meal.requested_at:
                deadline = max(deadline, (meal.dispensed_at or meal.requested_at) + DISPENSE_WAIT)
            if now >= deadline:
                if photo_pet_id is not None:
                    continue
                if meal is None:
                    meal = PetMeal(id=request_id, device_id=settings.device_id,
                                   scheduled_at=due, pet_id=pet.id, status="pending")
                    session.add(meal)
                alert_type, message = _expire(session, meal, pet, local_due)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    return None, "Cữ này đang được xử lý."
                await ws_manager.broadcast({"topic": "alert", "data": {
                    "type": alert_type, "message": message,
                }})
                await send_push("Cảnh báo cữ ăn", message)
                continue
            ready = photo_pet_id == pet.id or (
                presence and presence[0] == pet.id and presence[2] - presence[1] >= 2
            )
            if meal is not None or not ready:
                continue
            if not pet.auto_feed:
                blocked_reason = "Tính năng tự động cho ăn đang tắt cho thú cưng này."
                continue
            if device_busy:
                blocked_reason = "Máy vừa nhận một yêu cầu nhả. Vui lòng đợi 60 giây từ yêu cầu đó."
                continue
            if not latest or now - latest.created_at > WEIGHT_MAX_AGE or not math.isfinite(latest.value) or latest.value < 0:
                blocked_reason = "Chưa có số cân bát hợp lệ trong 12 giây gần nhất. Kiểm tra cân và kết nối ESP32."
                continue
            empty_limit = min(5, schedule.grams * 0.5)
            if latest.value >= empty_limit:
                blocked_reason = f"Bát đang có {latest.value:g} g. Cữ này yêu cầu bát còn dưới {empty_limit:g} g."
                continue
            day_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            day_start = day_start.astimezone(timezone.utc).replace(tzinfo=None)
            fed_today, last_eaten = (await session.execute(select(
                func.coalesce(func.sum(PetMeal.grams).filter(PetMeal.requested_at >= day_start), 0),
                func.max(PetMeal.eaten_at),
            ).where(PetMeal.device_id == settings.device_id, PetMeal.pet_id == pet.id))).one()
            if fed_today + schedule.grams > pet.daily_limit_grams:
                blocked_reason = "Khẩu phần của cữ này vượt giới hạn trong ngày của thú cưng."
                continue
            if last_eaten and now - last_eaten < timedelta(minutes=pet.min_feed_interval_min):
                ends = last_eaten + timedelta(minutes=pet.min_feed_interval_min)
                ends_local = ends.replace(tzinfo=timezone.utc).astimezone(LOCAL_TIME)
                blocked_reason = f"Thú cưng đang trong cooldown đến {ends_local:%H:%M:%S} (giờ Việt Nam)."
                continue
            session.add(PetMeal(
                id=request_id, device_id=settings.device_id, pet_id=pet.id,
                scheduled_at=due, requested_at=now, grams=schedule.grams, status="requested",
            ))
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return None, "Cữ này đang được xử lý."
            current = pipeline.feeding_presence() if pipeline is not None else None
            if photo_pet_id is not None or (
                current and current[0] == pet.id and current[1] == presence[1] and time.time() - current[2] <= 3
            ):
                published = await publish_command("PET_FEED", {
                    "id": request_id, "g": schedule.grams, "until": int(time.time()) + 10,
                })
                if published:
                    return request_id, ""
                return None, "Server không xác nhận được việc gửi lệnh đến MQTT. Kiểm tra máy và kết nối MQTT."
            return None, "Camera không còn xác nhận thú cưng đang đứng trước bát."
        return None, blocked_reason


async def monitor_pet_meals(pipeline):
    while True:
        try:
            async with _meal_check_lock:
                await _check_meals(pipeline)
        except Exception:
            logger.exception("Failed to check assigned pet meals")
        await asyncio.sleep(2)
