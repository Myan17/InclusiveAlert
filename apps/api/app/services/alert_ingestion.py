# apps/api/app/services/alert_ingestion.py
import uuid
import logging
from datetime import datetime, timezone
from typing import Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.hazard_event import HazardEvent

logger = logging.getLogger(__name__)

NWS_ALERTS_URL = "https://api.weather.gov/alerts/active?status=actual&message_type=alert"
USGS_EARTHQUAKES_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_hour.geojson"

SEVERITY_MAP = {"extreme": "extreme", "severe": "severe", "moderate": "moderate", "minor": "minor"}


def _usgs_magnitude_to_severity(mag: float) -> str:
    if mag >= 6.0:
        return "severe"
    if mag >= 5.0:
        return "moderate"
    if mag >= 4.0:
        return "minor"
    return "unknown"


def normalize_nws_alert(feature: dict) -> dict:
    props = feature.get("properties", {})
    event_name = props.get("event", "unknown").lower().replace(" ", "_")
    return {
        "external_id": feature["id"],
        "source": "nws",
        "hazard_type": event_name,
        "severity": SEVERITY_MAP.get(props.get("severity", "").lower(), "unknown"),
        "certainty": props.get("certainty", "unknown").lower(),
        "urgency": props.get("urgency", "unknown").lower(),
        "headline": props.get("headline"),
        "description": props.get("description"),
        "instruction": props.get("instruction"),
        "area_description": props.get("areaDesc"),
        "effective_at": _parse_dt(props.get("effective")),
        "expires_at": _parse_dt(props.get("expires")),
        "source_confidence": 1.0,
        "raw_payload": feature,
        "geometry_wkt": None,  # NWS polygons need separate processing
    }


def normalize_usgs_event(feature: dict) -> dict:
    props = feature.get("properties", {})
    mag = props.get("mag", 0.0) or 0.0
    ts = props.get("time", 0) / 1000
    geom = feature.get("geometry")
    coords = geom["coordinates"] if geom and geom.get("type") == "Point" else None
    return {
        "external_id": feature["id"],
        "source": "usgs",
        "hazard_type": "earthquake",
        "severity": _usgs_magnitude_to_severity(mag),
        "certainty": "observed",
        "urgency": "immediate" if mag >= 5.5 else "expected",
        "headline": props.get("title"),
        "description": props.get("place"),
        "instruction": None,
        "area_description": props.get("place"),
        "effective_at": datetime.fromtimestamp(ts, tz=timezone.utc),
        "expires_at": None,
        "source_confidence": 1.0,
        "raw_payload": feature,
        # Geometry column is MULTIPOLYGON; store None for USGS points to avoid type mismatch
        "geometry_wkt": None,
    }


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


async def _upsert_event(db: AsyncSession, data: dict) -> HazardEvent | None:
    result = await db.execute(
        select(HazardEvent).where(HazardEvent.external_id == data["external_id"])
    )
    existing = result.scalar_one_or_none()
    if existing:
        return None  # already stored

    geom_value = None
    if data.get("geometry_wkt"):
        from geoalchemy2.shape import from_shape
        from shapely import wkt as shapely_wkt
        try:
            shape = shapely_wkt.loads(data["geometry_wkt"])
            geom_value = from_shape(shape, srid=4326)
        except Exception:
            pass

    event = HazardEvent(
        id=uuid.uuid4(),
        external_id=data["external_id"],
        source=data["source"],
        hazard_type=data["hazard_type"],
        severity=data["severity"],
        certainty=data["certainty"],
        urgency=data["urgency"],
        headline=data.get("headline"),
        description=data.get("description"),
        instruction=data.get("instruction"),
        area_description=data.get("area_description"),
        effective_at=data["effective_at"] or datetime.now(timezone.utc),
        expires_at=data.get("expires_at"),
        source_confidence=data.get("source_confidence", 1.0),
        raw_payload=data.get("raw_payload"),
        geometry=geom_value,
    )
    db.add(event)
    return event


async def fetch_and_store_nws_alerts() -> int:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(
                NWS_ALERTS_URL,
                headers={"User-Agent": "InclusiveAlert/0.1 contact@inclusivealert.dev"},
            )
            resp.raise_for_status()
            features = resp.json().get("features", [])
        except Exception as e:
            logger.error(f"NWS fetch failed: {e}")
            return 0

    count = 0
    async with AsyncSessionLocal() as db:
        for feature in features:
            data = normalize_nws_alert(feature)
            result = await _upsert_event(db, data)
            if result:
                count += 1
        await db.commit()  # single commit for all new events
    logger.info(f"NWS: ingested {count} new alerts (checked {len(features)})")
    return count


async def fetch_and_store_usgs_events() -> int:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(USGS_EARTHQUAKES_URL)
            resp.raise_for_status()
            features = resp.json().get("features", [])
        except Exception as e:
            logger.error(f"USGS fetch failed: {e}")
            return 0

    count = 0
    async with AsyncSessionLocal() as db:
        for feature in features:
            if feature.get("properties", {}).get("mag", 0) < 2.5:
                continue
            data = normalize_usgs_event(feature)
            result = await _upsert_event(db, data)
            if result:
                count += 1
        await db.commit()  # single commit for all new events
    logger.info(f"USGS: ingested {count} new events (checked {len(features)})")
    return count
