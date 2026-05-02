# apps/api/app/routers/matching.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app.deps import get_current_user
from app.models.user_profile import UserProfile
from app.models.respondent_profile import RespondentProfile
from app.schemas.match_assignment import (
    MatchAssignmentResponse, MatchResult, MatchBreakdown,
    VictimListResponse, VictimSummary,
)
from app.services.matching_engine import rank_respondents

router = APIRouter(prefix="/matching", tags=["matching"])


@router.get("/assign", response_model=MatchAssignmentResponse)
async def assign_respondents(
    lat: float = Query(..., description="Victim's current latitude"),
    lon: float = Query(..., description="Victim's current longitude"),
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Rank available respondents for the current victim by MatchScore."""
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


@router.get("/victims", response_model=VictimListResponse)
async def list_victims_needing_help(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """
    For respondents and authority: list victims who have disability needs set.
    Sorted by urgency score (power_dependent + active needs count).
    """
    if current_user.role not in ("respondent", "authority"):
        raise HTTPException(status_code=403, detail="Respondent or authority role required")

    result = await db.execute(
        select(UserProfile).where(
            UserProfile.role == "victim",
            UserProfile.is_active == True,
        )
    )
    victims = result.scalars().all()

    summaries = []
    for v in victims:
        needs = v.disability_needs or []
        # Urgency: power_dependent is highest risk, each need adds weight
        urgency = 0.0
        if v.power_dependency:
            urgency += 0.4
        if "deaf" in needs:
            urgency += 0.15
        if "blind" in needs:
            urgency += 0.15
        if "mobility_wheelchair" in needs:
            urgency += 0.15
        urgency += min(0.15, len(needs) * 0.05)
        urgency = round(min(1.0, urgency), 3)

        summaries.append(VictimSummary(
            user_id=str(v.id),
            email=v.email,
            disability_needs=needs,
            communication_modes=v.communication_modes or [],
            service_animal=v.service_animal or False,
            power_dependency=v.power_dependency or False,
            location_zip=v.location_zip,
            location_city=v.location_city,
            location_state=v.location_state,
            urgency_score=urgency,
        ))

    summaries.sort(key=lambda x: x.urgency_score, reverse=True)
    return VictimListResponse(victims=summaries, total=len(summaries))
