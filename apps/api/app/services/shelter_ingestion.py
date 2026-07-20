# apps/api/app/services/shelter_ingestion.py
"""Sync real shelters from the FEMA National Shelter System (NSS) ArcGIS feed
into the shelters table. Accessibility values are tri-state: YES→True, NO→False,
anything else (UNK/blank)→None (unconfirmed). Authority-verified accessibility is
never overwritten by the feed."""
import uuid
import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.shelter import Shelter

logger = logging.getLogger(__name__)

FEMA_NSS_LAYERS = [0, 3]  # 0 = Open Shelters, 3 = Alert Shelters
FEMA_FIELDS = (
    "shelter_id,shelter_name,address_1,city,state,zip,evacuation_capacity,"
    "total_population,ada_compliant,wheelchair_accessible,generator_onsite,"
    "pet_accommodations_desc,latitude,longitude,org_main_phone,shelter_status_code"
)


def _yn(v) -> bool | None:
    """FEMA accessibility flags: YES→True, NO→False, UNK/blank/None→None."""
    if v is None:
        return None
    s = str(v).strip().upper()
    if s == "YES":
        return True
    if s == "NO":
        return False
    return None


def _pet_policy(desc: str | None) -> str:
    if not desc or not str(desc).strip():
        return "unknown"
    d = str(desc).lower()
    if "service" in d:
        return "service_animals_only"
    if "no pet" in d or "not allow" in d:
        return "no_pets"
    if "pet" in d:
        return "pets_allowed"
    return "unknown"


def _status(code: str | None) -> str:
    if not code:
        return "open"
    return {"OPEN": "open", "CLOSED": "closed", "FULL": "full"}.get(str(code).strip().upper(), "open")


def normalize_fema_shelter(attrs: dict) -> dict:
    parts = [attrs.get("address_1"), attrs.get("city"), attrs.get("state"), attrs.get("zip")]
    address = ", ".join(str(p).strip() for p in parts if p and str(p).strip())
    return {
        "external_id": str(attrs["shelter_id"]),
        "name": attrs.get("shelter_name") or "Unnamed Shelter",
        "address": address or None,
        "lat": attrs.get("latitude"),
        "lon": attrs.get("longitude"),
        "capacity": attrs.get("evacuation_capacity"),
        "current_occupancy": attrs.get("total_population"),
        "status": _status(attrs.get("shelter_status_code")),
        "wheelchair_accessible": _yn(attrs.get("wheelchair_accessible")),
        "ada_compliant": _yn(attrs.get("ada_compliant")),
        "generator_onsite": _yn(attrs.get("generator_onsite")),
        "asl_support": None,  # ASL is never in the FEMA feed — authorities confirm it
        "pet_policy": _pet_policy(attrs.get("pet_accommodations_desc")),
        "phone": attrs.get("org_main_phone"),
        "source": "fema_nss",
    }


def _make_location(lat, lon):
    if lat is None or lon is None:
        return None
    try:
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point
        return from_shape(Point(float(lon), float(lat)), srid=4326)
    except Exception:
        return None


def _set_location(shelter: Shelter, lat, lon) -> None:
    if hasattr(type(shelter), "location"):
        shelter.location = _make_location(lat, lon)


async def _upsert_shelter(db: AsyncSession, data: dict) -> Shelter:
    """Insert a new shelter or refresh an existing one (by external_id).
    Operational fields (capacity/occupancy/status/location/phone) always refresh;
    accessibility fields refresh only when the shelter is NOT authority-verified."""
    now = datetime.now(timezone.utc)
    existing = (
        await db.execute(select(Shelter).where(Shelter.external_id == data["external_id"]))
    ).scalar_one_or_none()

    if existing is not None:
        existing.capacity = data.get("capacity")
        existing.current_occupancy = data.get("current_occupancy")
        existing.status = data.get("status", existing.status)
        if data.get("phone"):
            existing.phone = data["phone"]
        if data.get("lat") is not None and data.get("lon") is not None:
            existing.lat, existing.lon = data["lat"], data["lon"]
            _set_location(existing, data["lat"], data["lon"])
        existing.last_synced_at = now
        if existing.verified_by is None:  # human confirmation always wins
            existing.wheelchair_accessible = data.get("wheelchair_accessible")
            existing.ada_compliant = data.get("ada_compliant")
            existing.generator_onsite = data.get("generator_onsite")
            existing.asl_support = data.get("asl_support")
            existing.pet_policy = data.get("pet_policy", "unknown")
        return existing

    shelter = Shelter(
        id=uuid.uuid4(),
        external_id=data["external_id"],
        name=data["name"],
        address=data.get("address"),
        lat=data.get("lat"),
        lon=data.get("lon"),
        status=data.get("status", "open"),
        capacity=data.get("capacity"),
        current_occupancy=data.get("current_occupancy"),
        wheelchair_accessible=data.get("wheelchair_accessible"),
        ada_compliant=data.get("ada_compliant"),
        generator_onsite=data.get("generator_onsite"),
        asl_support=data.get("asl_support"),
        pet_policy=data.get("pet_policy", "unknown"),
        source="fema_nss",
        phone=data.get("phone"),
        last_synced_at=now,
    )
    _set_location(shelter, data.get("lat"), data.get("lon"))
    db.add(shelter)
    return shelter


async def fetch_and_store_fema_shelters() -> int:
    features: list[dict] = []
    async with httpx.AsyncClient(timeout=40.0) as client:
        for layer in FEMA_NSS_LAYERS:
            url = (
                f"https://gis.fema.gov/arcgis/rest/services/NSS/FEMA_NSS/MapServer/{layer}/query"
                f"?where=1%3D1&outFields={FEMA_FIELDS}&f=json&resultRecordCount=2000"
            )
            try:
                resp = await client.get(
                    url, headers={"User-Agent": "InclusiveAlert/0.1 contact@inclusivealert.dev"}
                )
                resp.raise_for_status()
                features.extend(resp.json().get("features", []))
            except Exception as e:
                logger.error(f"FEMA NSS layer {layer} fetch failed: {e}")

    count = 0
    async with AsyncSessionLocal() as db:
        for feat in features:
            attrs = feat.get("attributes", {})
            if not attrs.get("shelter_id") or attrs.get("latitude") is None:
                continue
            await _upsert_shelter(db, normalize_fema_shelter(attrs))
            count += 1
        await db.commit()
    logger.info(f"FEMA NSS: synced {count} shelters")
    return count
