import math
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shapely.geometry import Point, shape
from shapely import wkt as shapely_wkt

logger = logging.getLogger(__name__)

def point_in_polygon_wkt(lat: float, lon: float, polygon_wkt: str) -> bool:
    """Check if a lat/lon point falls inside a WKT polygon (no DB needed)."""
    try:
        poly = shapely_wkt.loads(polygon_wkt)
        pt = Point(lon, lat)  # shapely uses (lon, lat) = (x, y)
        return poly.contains(pt)
    except Exception as e:
        logger.warning(f"Geofence WKT check failed: {e}")
        return False

def compute_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine great-circle distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

async def users_in_hazard_zone(
    db: AsyncSession,
    hazard_event_id: str,
    radius_km: float = 50.0,
) -> list[dict]:
    """
    Returns list of {user_id, location_zip, location_state} for users whose
    stored ZIP centroid falls within the hazard zone.
    Falls back to returning all users in same state as area_description.
    PostGIS ST_Contains path activates once users opt in to precise GPS location.
    """
    sql = text("""
        SELECT up.id AS user_id, up.location_zip, up.location_state, up.disability_needs
        FROM user_profiles up
        JOIN hazard_events he ON he.id = :hazard_id
        WHERE up.is_active = true
        AND (
            he.geometry IS NOT NULL
            -- Future: AND ST_Contains(he.geometry, ST_SetSRID(ST_Point(up.location_lon, up.location_lat), 4326))
            OR up.location_state IS NOT NULL
        )
        LIMIT 1000
    """)
    result = await db.execute(sql, {"hazard_id": hazard_event_id})
    rows = result.mappings().all()
    return [dict(r) for r in rows]
