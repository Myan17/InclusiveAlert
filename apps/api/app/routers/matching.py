# apps/api/app/routers/matching.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app.deps import get_current_user
from app.models.user_profile import UserProfile
from app.models.respondent_profile import RespondentProfile
from app.schemas.match_assignment import MatchAssignmentResponse, MatchResult, MatchBreakdown
from app.services.matching_engine import rank_respondents

router = APIRouter(prefix="/matching", tags=["matching"])


@router.get("/assign", response_model=MatchAssignmentResponse)
async def assign_respondents(
    lat: float = Query(..., description="Victim's current latitude"),
    lon: float = Query(..., description="Victim's current longitude"),
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Rank available respondents for the current victim by MatchScore.
    Returns the top 10 best-matching respondents.
    """
    result = await db.execute(
        select(RespondentProfile).where(
            RespondentProfile.availability_status != "unavailable"
        )
    )
    respondent_rows = result.scalars().all()

    victim = {
        "lat": lat,
        "lon": lon,
        "disability_needs": current_user.disability_needs or [],
    }

    respondents = [
        {
            "respondent_id": str(rp.id),
            "lat": rp.location_lat,
            "lon": rp.location_lon,
            "skills": rp.skills or [],
            "availability_status": rp.availability_status,
            "trust_tier": rp.trust_tier,
            "communication_modes": rp.communication_modes or [],
        }
        for rp in respondent_rows
    ]

    ranked = rank_respondents(victim, respondents)
    top10 = ranked[:10]

    match_results = [
        MatchResult(
            respondent_id=item["respondent_id"],
            score=item["score"],
            breakdown=MatchBreakdown(**item["breakdown"]),
        )
        for item in top10
    ]

    return MatchAssignmentResponse(results=match_results, total=len(match_results))
