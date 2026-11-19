import logging
import os

logger = logging.getLogger("push")

_fcm_initialized = False


def _init_fcm():
    global _fcm_initialized
    if _fcm_initialized:
        return True
    try:
        from ..config import settings
        cred_path = settings.fcm_credentials_path
        if not os.path.exists(cred_path):
            logger.info("FCM credentials not found at %s — push disabled", cred_path)
            return False
        import firebase_admin
        from firebase_admin import credentials
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _fcm_initialized = True
        logger.info("FCM initialized")
        return True
    except Exception as e:
        logger.warning("FCM init failed: %s", e)
        return False


async def send_push(title: str, body: str):
    if not _init_fcm():
        return

    from ..database import async_session
    from ..models import FCMToken
    from sqlalchemy import select

    try:
        from firebase_admin import messaging

        async with async_session() as session:
            result = await session.execute(select(FCMToken))
            tokens = [row.token for row in result.scalars().all()]

        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
        )
        response = messaging.send_each_for_multicast(message)
        logger.info("Push sent: %d success, %d fail",
                     response.success_count, response.failure_count)
    except Exception as e:
        logger.warning("Push failed: %s", e)
