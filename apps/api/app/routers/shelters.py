from fastapi import APIRouter, Depends, Query
from app.deps import get_current_user
from app.models.user_profile import UserProfile
from app.schemas.shelter import ShelterResponse
from app.services.shelter_ranking import fetch_fema_shelters, rank_shelters

router = APIRouter(prefix="/shelters", tags=["shelters"])

@router.get("/ranked", response_model=list[ShelterResponse])
async def get_ranked_shelters(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius_km: float = Query(80.0, le=200.0),
    current_user: UserProfile = Depends(get_current_user),
):
    shelters = await fetch_fema_shelters(lat, lon, radius_km)
    if not shelters:
        return []
    victim_needs = {
        "disability_needs": current_user.disability_needs or [],
        "service_animal": current_user.service_animal or False,
    }
    ranked = rank_shelters(shelters, victim_needs)
    return ranked[:10]  # top 10
