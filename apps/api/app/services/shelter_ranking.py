import math
import logging
from typing import Any
import httpx
from app.services.geofence import compute_distance_km

logger = logging.getLogger(__name__)

def _distance_score(distance_km: float) -> float:
    """Closer = higher score. 0km → 1.0, 50km → ~0.0"""
    return max(0.0, 1.0 - (distance_km / 50.0))

def _accessibility_fit_score(shelter: dict, victim_needs: dict) -> float:
    score = 1.0
    needs = set(victim_needs.get("disability_needs", []))

    if "mobility_wheelchair" in needs and not shelter.get("wheelchair_accessible"):
        score -= 0.5  # critical miss
    if "mobility_wheelchair" in needs and not shelter.get("ada_compliant"):
        score -= 0.2
    if "power_dependent" in needs and not shelter.get("generator_onsite"):
        score -= 0.4  # critical miss for oxygen/ventilator users
    if victim_needs.get("service_animal") and shelter.get("pet_policy") == "no_pets":
        score -= 0.3  # service animals are a legal right, but flag if listed as no_pets
    if "deaf" in needs and not shelter.get("asl_support", False):
        score -= 0.1

    return max(0.0, score)

def _capacity_score(shelter: dict) -> float:
    if shelter.get("status") == "closed":
        return 0.0
    if shelter.get("status") == "full":
        return 0.1
    capacity = shelter.get("capacity") or 0
    occupancy = shelter.get("current_occupancy") or 0
    if capacity == 0:
        return 0.5  # unknown — neutral
    utilization = occupancy / capacity
    return max(0.0, 1.0 - utilization)

def _freshness_score(days_ago: int) -> float:
    """Verification recency: same-day = 1.0, 30+ days = 0.2"""
    return max(0.2, 1.0 - (days_ago / 30.0))

def compute_shelter_score(shelter: dict, victim_needs: dict) -> float:
    distance = _distance_score(shelter.get("distance_km", 25.0))
    hazard_safety = shelter.get("hazard_safety_score", 0.5)
    accessibility = _accessibility_fit_score(shelter, victim_needs)
    power = 1.0 if shelter.get("generator_onsite") else 0.2
    capacity = _capacity_score(shelter)
    transport = shelter.get("transport_feasibility", 0.5)
    freshness = _freshness_score(shelter.get("last_verified_days_ago", 7))

    score = (
        0.20 * distance +
        0.20 * hazard_safety +
        0.20 * accessibility +
        0.15 * power +
        0.10 * capacity +
        0.10 * transport +
        0.05 * freshness
    )
    return round(min(1.0, max(0.0, score)), 4)

def rank_shelters(shelters: list[dict], victim_needs: dict) -> list[dict]:
    for s in shelters:
        s["shelter_score"] = compute_shelter_score(s, victim_needs)
    return sorted(shelters, key=lambda x: x["shelter_score"], reverse=True)

async def fetch_fema_shelters(lat: float, lon: float, radius_km: float = 80.0) -> list[dict]:
    """Fetch open shelters from FEMA NSS ArcGIS REST API."""
    url = (
        f"https://gis.fema.gov/arcgis/rest/services/NSS/FEMA_NSS/MapServer/3/query"
        f"?where=SHELTER_STATUS='Open'&outFields=SHELTER_NAME,ADDRESS,CITY,STATE,"
        f"WHEELCHAIR,ADA_COMPLIANT,GENERATOR,PET_ACCOMMODATIONS,TOTAL_CAPACITY,"
        f"OCCUPANCY_COUNT,LATITUDE,LONGITUDE"
        f"&geometry={lon},{lat}&geometryType=esriGeometryPoint"
        f"&distance={radius_km * 1000}&inSR=4326&spatialRel=esriSpatialRelIntersects"
        f"&outSR=4326&f=json&resultRecordCount=50"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            features = resp.json().get("features", [])
    except Exception as e:
        logger.error(f"FEMA NSS fetch failed: {e}")
        return []

    shelters = []
    for f in features:
        attrs = f.get("attributes", {})
        geom = f.get("geometry", {})
        s_lat = attrs.get("LATITUDE") or geom.get("y")
        s_lon = attrs.get("LONGITUDE") or geom.get("x")
        if not s_lat or not s_lon:
            continue
        dist = compute_distance_km(lat, lon, float(s_lat), float(s_lon))
        shelters.append({
            "name": attrs.get("SHELTER_NAME", "Unknown Shelter"),
            "address": f"{attrs.get('ADDRESS','')}, {attrs.get('CITY','')}, {attrs.get('STATE','')}",
            "distance_km": dist,
            "wheelchair_accessible": attrs.get("WHEELCHAIR") == "Yes",
            "ada_compliant": attrs.get("ADA_COMPLIANT") == "Yes",
            "generator_onsite": attrs.get("GENERATOR") == "Yes",
            "pet_policy": "pets_allowed" if attrs.get("PET_ACCOMMODATIONS") == "Yes" else "no_pets",
            "status": "open",
            "capacity": attrs.get("TOTAL_CAPACITY"),
            "current_occupancy": attrs.get("OCCUPANCY_COUNT"),
            "hazard_safety_score": 0.8,
            "transport_feasibility": 0.7,
            "last_verified_days_ago": 0,
            "lat": s_lat,
            "lon": s_lon,
            "source": "fema_nss",
        })
    return shelters
