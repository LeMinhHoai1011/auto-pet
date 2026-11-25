from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import AlertLog, Pet, PetMeal, Schedule, SchedulePet, SensorLog
from app.services import pet_meals


class PetMealTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.addAsyncCleanup(self.engine.dispose)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.now = datetime(2026, 11, 25, 0, 2)
        self.device = pet_meals.settings.device_id
        async with self.sessions.begin() as session:
            session.add_all([Pet(id=1, name="Miu"), Pet(id=2, name="Mun")])
            for hour, minute, pet_id in [(7, 0, 1), (7, 5, 2), (7, 10, 1), (9, 0, 1)]:
                session.add(Schedule(
                    device_id=self.device, hour=hour, minute=minute, grams=30,
                    created_at=self.now - timedelta(hours=2),
                    assignment=SchedulePet(key=f"{hour}:{minute}", pet_id=pet_id),
                ))
        self.camera = SimpleNamespace(feeding_presence=lambda: self.presence)
        self.presence = None
        self.publish = AsyncMock(return_value=True)
        for mock in (
            patch.object(pet_meals, "async_session", self.sessions),
            patch.object(pet_meals, "datetime", SimpleNamespace(utcnow=lambda: self.now)),
            patch.object(pet_meals, "time", SimpleNamespace(time=lambda: pet_meals._epoch(self.now))),
            patch.object(pet_meals, "publish_command", self.publish),
            patch.object(pet_meals, "send_push", AsyncMock()),
        ):
            mock.start()
            self.addCleanup(mock.stop)

    def see(self, pet_id, seconds=10):
        now = pet_meals._epoch(self.now)
        self.presence = (pet_id, now - seconds, now)

    async def weigh(self, grams, seconds_ago=0):
        async with self.sessions.begin() as session:
            session.add(SensorLog(
                device_id=self.device, sensor_type="weight", unit="g", value=grams,
                created_at=self.now - timedelta(seconds=seconds_ago),
            ))

    async def test_confirmed_eating_sets_cooldown_and_missed_meal_names_pet(self):
        await self.weigh(1)
        await pet_meals._check_meals(self.camera)
        self.publish.assert_not_awaited()

        self.see(1)
        await pet_meals._check_meals(self.camera)
        await pet_meals._check_meals(self.camera)
        self.publish.assert_awaited_once()
        command, data = self.publish.await_args.args
        self.assertEqual(command, "PET_FEED")
        request_id = data["id"]
        async with self.sessions.begin() as session:
            await pet_meals.record_dispense(session, {"id": request_id, "actual_g": 29})

        self.now += timedelta(seconds=20)
        await self.weigh(30, seconds_ago=15)
        await self.weigh(23, seconds_ago=5)
        await self.weigh(22)
        self.see(2, seconds=20)
        await pet_meals._check_meals(self.camera)
        async with self.sessions() as session:
            self.assertEqual((await session.get(PetMeal, request_id)).status, "dispensed")

        self.see(1, seconds=20)
        await pet_meals._check_meals(self.camera)
        async with self.sessions() as session:
            self.assertEqual((await session.get(PetMeal, request_id)).status, "eaten")

        self.now = self.now.replace(minute=12)
        self.see(1)
        await self.weigh(1)
        await pet_meals._check_meals(self.camera)
        self.publish.assert_awaited_once()

        self.now = self.now.replace(minute=41)
        self.presence = None
        await pet_meals._check_meals(self.camera)
        await pet_meals._check_meals(self.camera)
        async with self.sessions() as session:
            alerts = (await session.scalars(select(AlertLog.message))).all()
            self.assertEqual(alerts.count("Mun chưa ăn cữ 07:05."), 1)

        self.now = self.now.replace(hour=2, minute=3)
        self.see(1)
        await self.weigh(1)
        await pet_meals._check_meals(self.camera)
        self.assertEqual(self.publish.await_count, 2)

    async def test_other_registered_pet_can_eat_during_mius_cooldown(self):
        async with self.sessions.begin() as session:
            session.add(PetMeal(
                id="previous-meal", device_id=self.device, pet_id=1,
                scheduled_at=self.now, eaten_at=self.now, grams=30, status="eaten",
            ))
        self.now += timedelta(minutes=5)
        await self.weigh(1)
        self.see(2)
        await pet_meals._check_meals(self.camera)
        self.publish.assert_awaited_once()
        _, data = self.publish.await_args.args
        async with self.sessions() as session:
            self.assertEqual((await session.get(PetMeal, data["id"])).pet_id, 2)

    async def test_photo_can_request_one_meal_without_camera_and_cannot_confirm_eating(self):
        async with self.sessions.begin() as session:
            schedule = await session.scalar(select(Schedule).where(Schedule.hour == 7, Schedule.minute == 0))
            schedule.created_at = self.now
        self.assertIn("12 giây", (await pet_meals.request_photo_feed(1))[1])
        await self.weigh(15)
        self.assertIn("15 g", (await pet_meals.request_photo_feed(1))[1])
        await self.weigh(1)
        self.assertEqual(await pet_meals.request_photo_feed(2), (None, pet_meals.NO_OPEN_MEAL))
        request_id, reason = await pet_meals.request_photo_feed(1)
        self.assertIsNotNone(request_id)
        self.assertEqual(reason, "")
        self.assertIn("đã có yêu cầu", (await pet_meals.request_photo_feed(1))[1])
        self.publish.assert_awaited_once()

        async with self.sessions.begin() as session:
            await pet_meals.record_dispense(session, {"id": request_id, "actual_g": 29})
        self.now += timedelta(seconds=20)
        await self.weigh(30, seconds_ago=15)
        await self.weigh(23, seconds_ago=5)
        await self.weigh(22)
        self.assertIsNone((await pet_meals.request_photo_feed(1))[0])
        async with self.sessions() as session:
            meal = await session.get(PetMeal, request_id)
            self.assertEqual(meal.status, "dispensed")
            self.assertIsNone(meal.eaten_at)
