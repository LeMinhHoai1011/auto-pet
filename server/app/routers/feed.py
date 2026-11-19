from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models import FeedingLog
from ..schemas import FeedRequest, FeedingOut
from ..services.mqtt_publisher import publish_command

router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.post("/")
async def trigger_feed(req: FeedRequest):
    ok = await publish_command("FEED", {"g": req.grams})
    return {"ok": ok, "grams": req.grams}


@router.post("/tare")
async def trigger_tare():
    ok = await publish_command("TARE")
    return {"ok": ok}


@router.get("/history", response_model=list[FeedingOut])
async def feed_history(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeedingLog)
        .where(FeedingLog.device_id == settings.device_id)
        .order_by(FeedingLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()
