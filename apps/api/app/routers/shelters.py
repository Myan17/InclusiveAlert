import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.deps import get_current_user
from app.database import get_async_session
from app.models.user_profile import UserProfile
from app.models.shelter import Shelter
from app.schemas.shelter import ShelterResponse
from app.services.shelter_ranking import fetch_fema_shelters, rank_shelters, compute_shelter_score
from app.services.geofence import compute_distance_km

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shelters", tags=["shelters"])

async def _postgis_available(db: AsyncSession) -> bool:
    try:
        result = await db.execute(text("SELECT 1 FROM pg_extension WHERE extname='postgis'"))
        return result.scalar() is not None
    except Exception:
        return False

@router.get("/ranked", response_model=list[ShelterResponse])
async def get_ranked_shelters(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius_km: float = Query(80.0, le=200.0),
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    victim_needs = {
        "disability_needs": current_user.disability_needs or [],
        "service_animal": current_user.service_animal or False,
    }

    has_postgis = await _postgis_available(db)

    # 1. Try DB shelters first
    db_shelters = []
    try:
        if has_postgis:
            from geoalchemy2.functions import ST_X, ST_Y
            result = await db.execute(
                select(
                    Shelter,
                    ST_X(Shelter.location).label("lon"),
                    ST_Y(Shelter.location).label("lat"),
                ).where(Shelter.status != "closed")
            )
            rows = result.all()
            for row in rows:
                shelter, s_lon, s_lat = row
                dist = compute_distance_km(lat, lon, float(s_lat), float(s_lon))
                if dist > radius_km:
                    continue
                db_shelters.append({
                    "name": shelter.name,
                    "address": shelter.address,
                    "distance_km": dist,
                    "wheelchair_accessible": shelter.wheelchair_accessible,
                    "ada_compliant": shelter.ada_compliant,
                    "generator_onsite": shelter.generator_onsite,
                    "pet_policy": shelter.pet_policy,
                    "asl_support": shelter.asl_support,
                    "status": shelter.status,
                    "capacity": shelter.capacity,
                    "current_occupancy": shelter.current_occupancy,
                    "hazard_safety_score": 0.8,
                    "transport_feasibility": 0.7,
                    "last_verified_days_ago": 0,
                    "lat": float(s_lat),
                    "lon": float(s_lon),
                    "source": shelter.source or "db",
                })
        else:
            # No PostGIS — use lat/lon columns directly
            result = await db.execute(
                select(Shelter).where(Shelter.status != "closed")
            )
            rows = result.scalars().all()
            for shelter in rows:
                s_lat = getattr(shelter, 'lat', None)
                s_lon = getattr(shelter, 'lon', None)
                if s_lat is None or s_lon is None:
                    continue
                dist = compute_distance_km(lat, lon, float(s_lat), float(s_lon))
                if dist > radius_km:
                    continue
                db_shelters.append({
                    "name": shelter.name,
                    "address": shelter.address,
                    "distance_km": dist,
                    "wheelchair_accessible": shelter.wheelchair_accessible,
                    "ada_compliant": shelter.ada_compliant,
                    "generator_onsite": shelter.generator_onsite,
                    "pet_policy": shelter.pet_policy,
                    "asl_support": shelter.asl_support,
                    "status": shelter.status,
                    "capacity": shelter.capacity,
                    "current_occupancy": shelter.current_occupancy,
                    "hazard_safety_score": 0.8,
                    "transport_feasibility": 0.7,
                    "last_verified_days_ago": 0,
                    "lat": float(s_lat),
                    "lon": float(s_lon),
                    "source": shelter.source or "db",
                })
    except Exception:
        # Don't let a DB read error silently fall through to the FEMA fallback
        # with no trace — surface it in logs (a schema/query bug hides here otherwise).
        logger.exception("DB shelter query failed; falling back to FEMA NSS")
        db_shelters = []

    if db_shelters:
        ranked = rank_shelters(db_shelters, victim_needs)
        return ranked[:10]

    # 2. Fall back to FEMA NSS live API
    shelters = await fetch_fema_shelters(lat, lon, radius_km)
    if not shelters:
        return []
    ranked = rank_shelters(shelters, victim_needs)
    return ranked[:10]
