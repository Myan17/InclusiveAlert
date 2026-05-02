# apps/api/app/routers/alerts.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.database import get_async_session
from app.models.hazard_event import HazardEvent
from app.schemas.hazard_event import HazardEventResponse
from app.deps import get_current_user
from app.models.user_profile import UserProfile

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/active", response_model=list[HazardEventResponse])
async def get_active_alerts(
    db: AsyncSession = Depends(get_async_session),
    _: UserProfile = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(HazardEvent)
        .where((HazardEvent.expires_at == None) | (HazardEvent.expires_at > now))
        .order_by(HazardEvent.effective_at.desc())
        .limit(100)
    )
    return result.scalars().all()


@router.get("/{alert_id}", response_model=HazardEventResponse)
async def get_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    _: UserProfile = Depends(get_current_user),
):
    result = await db.execute(select(HazardEvent).where(HazardEvent.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
