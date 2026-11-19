from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import FCMToken
from ..schemas import FCMTokenRegister

router = APIRouter(prefix="/api/push", tags=["push"])


@router.post("/register")
async def register_token(req: FCMTokenRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FCMToken).where(FCMToken.token == req.token))
    existing = result.scalar_one_or_none()
    if existing:
        return {"ok": True, "status": "already_registered"}
    db.add(FCMToken(token=req.token, device_name=req.device_name))
    await db.commit()
    return {"ok": True, "status": "registered"}


@router.delete("/unregister")
async def unregister_token(req: FCMTokenRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FCMToken).where(FCMToken.token == req.token))
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.commit()
    return {"ok": True}
