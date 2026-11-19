from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models import AlertLog
from ..schemas import AlertOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
async def list_alerts(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AlertLog)
        .where(AlertLog.device_id == settings.device_id)
        .order_by(AlertLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlertLog).where(AlertLog.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return {"ok": False, "error": "not found"}
    alert.resolved = True
    await db.commit()
    return {"ok": True}
