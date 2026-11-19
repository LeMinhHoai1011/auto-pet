"""Run in API image: python -m unittest discover -s tests -v."""
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import ValidationError
from app.schemas import FeedRequest, ScheduleCreate, ScheduleUpdate
from app.services import mqtt_service, mqtt_publisher


class ValidationTests(unittest.TestCase):
    def test_reject_invalid_schedule_and_feed(self):
        for values in ({"hour": 24, "minute": 0}, {"hour": 0, "minute": -1},
                       {"hour": 0, "minute": 0, "grams": 151},
                       {"hour": 0, "minute": 0, "grams": float("nan")}):
            with self.assertRaises(ValidationError):
                ScheduleCreate(**values)
        with self.assertRaises(ValidationError):
            FeedRequest(grams=0)
        with self.assertRaises(ValidationError):
            ScheduleUpdate(minute=60)


class MqttTests(unittest.IsolatedAsyncioTestCase):
    async def test_sensor_fields_match_firmware(self):
        session = MagicMock()
        session.commit = AsyncMock()
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=session)
        context.__aexit__ = AsyncMock(return_value=False)
        with patch.object(mqtt_service, "async_session", return_value=context), \
             patch.object(mqtt_service, "_upsert_device_state", new_callable=AsyncMock) as update:
            await mqtt_service._handle_message(mqtt_service.TOPIC_PREFIX + "sensor/weight", '{"bowl_g":42.5}')
            self.assertEqual(update.call_args.kwargs, {"bowl_grams": 42.5})
            await mqtt_service._handle_message(mqtt_service.TOPIC_PREFIX + "sensor/food_level", '{"hopper_pct":67}')
            self.assertEqual(update.call_args.kwargs, {"hopper_pct": 67})
            for state in ("online", "offline"):
                await mqtt_service._handle_message(mqtt_service.TOPIC_PREFIX + "status", state)
                self.assertEqual(update.call_args.kwargs, {"online": state == "online"})

    async def test_command_payload_and_failure(self):
        client = AsyncMock()
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=client)
        context.__aexit__ = AsyncMock(return_value=False)
        with patch.object(mqtt_publisher.aiomqtt, "Client", return_value=context):
            meals = [{"h": 7, "m": 30, "g": 35}]
            self.assertTrue(await mqtt_publisher.publish_command("SCHEDULE", {"meals": meals}))
            topic, body = client.publish.call_args.args
            self.assertTrue(topic.endswith("/command"))
            self.assertEqual(json.loads(body), {"cmd": "SCHEDULE", "meals": meals})
            client.publish.side_effect = ConnectionError("test disconnect")
            self.assertFalse(await mqtt_publisher.publish_command("STATUS"))


if __name__ == "__main__":
    unittest.main()
