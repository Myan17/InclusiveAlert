import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.deps import get_current_user
from app.database import get_async_session
from app.models.user_profile import UserProfile
from app.models.shelter import Shelter
from app.models.audit_event import AuditEvent
from app.schemas.shelter import ShelterResponse, ShelterCreate, ShelterUpdate, ShelterDetail
from app.services.shelter_ranking import fetch_fema_shelters, rank_shelters, compute_shelter_score
from app.services.shelter_ingestion import _set_location
from app.services.geofence import compute_distance_km

logger = logging.getLogger(__name__)


def _require_authority(user: UserProfile) -> None:
    if user.role != "authority":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authority role required")

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
                    "phone": shelter.phone,
                    "verified_by": shelter.verified_by,
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
                    "phone": shelter.phone,
                    "verified_by": shelter.verified_by,
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


@router.get("", response_model=list[ShelterDetail])
async def list_shelters(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
    limit: int = Query(200, le=500),
):
    """Authority list of shelters to review/enrich (includes ids for PATCH)."""
    _require_authority(current_user)
    rows = (
        await db.execute(select(Shelter).order_by(Shelter.name).limit(limit))
    ).scalars().all()
    return rows


@router.post("", response_model=ShelterDetail, status_code=status.HTTP_201_CREATED)
async def create_shelter(
    payload: ShelterCreate,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Authority-seeded facility (school, church, etc.), verified on creation."""
    _require_authority(current_user)
    now = datetime.now(timezone.utc)
    shelter = Shelter(
        id=uuid.uuid4(),
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lon=payload.lon,
        status=payload.status,
        capacity=payload.capacity,
        current_occupancy=payload.current_occupancy,
        wheelchair_accessible=payload.wheelchair_accessible,
        ada_compliant=payload.ada_compliant,
        generator_onsite=payload.generator_onsite,
        asl_support=payload.asl_support,
        pet_policy=payload.pet_policy,
        phone=payload.phone,
        source="authority",
        verified_by=current_user.id,
        last_verified_at=now,
    )
    _set_location(shelter, payload.lat, payload.lon)
    db.add(shelter)
    db.add(AuditEvent(actor_id=current_user.id, action="shelter.create",
                      data_category="shelter", details={"name": payload.name}))
    await db.commit()
    await db.refresh(shelter)
    return shelter


@router.patch("/{shelter_id}", response_model=ShelterDetail)
async def update_shelter(
    shelter_id: uuid.UUID,
    payload: ShelterUpdate,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    """Authority confirms/edits a shelter's accessibility; marks it verified."""
    _require_authority(current_user)
    shelter = (
        await db.execute(select(Shelter).where(Shelter.id == shelter_id))
    ).scalar_one_or_none()
    if shelter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shelter not found")

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(shelter, field, value)
    shelter.verified_by = current_user.id
    shelter.last_verified_at = datetime.now(timezone.utc)
    db.add(AuditEvent(actor_id=current_user.id, action="shelter.verify",
                      data_category="shelter", details={"shelter_id": str(shelter_id), "changes": changes}))
    await db.commit()
    await db.refresh(shelter)
    return shelter
