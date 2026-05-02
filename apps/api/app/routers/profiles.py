# apps/api/app/routers/profiles.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_async_session
from app.deps import get_current_user
from app.models.user_profile import UserProfile
from app.models.respondent_profile import RespondentProfile
from app.schemas.user_profile import VictimProfileUpdate, VictimProfileResponse
from app.schemas.respondent_profile import RespondentProfileCreate, RespondentProfileResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/victim", response_model=VictimProfileResponse)
async def upsert_victim_profile(
    data: VictimProfileUpdate,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/victim", response_model=VictimProfileResponse)
async def get_victim_profile(
    current_user: UserProfile = Depends(get_current_user),
):
    return current_user


@router.post("/respondent", response_model=RespondentProfileResponse)
async def upsert_respondent_profile(
    data: RespondentProfileCreate,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(RespondentProfile).where(RespondentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        profile = RespondentProfile(id=uuid.uuid4(), user_id=current_user.id, **data.model_dump())
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("/respondent", response_model=RespondentProfileResponse)
async def get_respondent_profile(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(RespondentProfile).where(RespondentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="No respondent profile found")
    return profile
