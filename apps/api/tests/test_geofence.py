import pytest
from app.services.geofence import (
    point_in_polygon_wkt,
    compute_distance_km,
    users_in_hazard_zone,
)

TORNADO_POLYGON_WKT = """POLYGON((
    -93.5 44.8, -93.0 44.8, -93.0 45.2, -93.5 45.2, -93.5 44.8
))"""

def test_point_inside_polygon():
    lat, lon = 45.0, -93.25  # Minneapolis area — inside polygon
    assert point_in_polygon_wkt(lat, lon, TORNADO_POLYGON_WKT) is True

def test_point_outside_polygon():
    lat, lon = 44.0, -93.25  # South of polygon
    assert point_in_polygon_wkt(lat, lon, TORNADO_POLYGON_WKT) is False

def test_compute_distance_km():
    # Minneapolis to St. Paul — approx 15km
    dist = compute_distance_km(44.9778, -93.2650, 44.9537, -93.0900)
    assert 14.0 < dist < 17.0

def test_distance_same_point():
    dist = compute_distance_km(45.0, -93.0, 45.0, -93.0)
    assert dist == pytest.approx(0.0, abs=0.001)
