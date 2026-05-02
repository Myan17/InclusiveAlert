# apps/api/tests/test_alert_ingestion.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.alert_ingestion import (
    normalize_nws_alert,
    normalize_usgs_event,
    fetch_and_store_nws_alerts,
)

NWS_ALERT_FIXTURE = {
    "id": "https://api.weather.gov/alerts/urn:oid:2.49.0.1.840.0.TEST",
    "properties": {
        "event": "Tornado Warning",
        "severity": "Extreme",
        "certainty": "Observed",
        "urgency": "Immediate",
        "headline": "Tornado Warning issued",
        "description": "A severe tornado is approaching.",
        "instruction": "Take shelter immediately.",
        "effective": "2026-05-01T12:00:00-05:00",
        "expires": "2026-05-01T12:45:00-05:00",
        "areaDesc": "Hennepin County, MN",
        "geocode": {"UGC": ["MNC053"]},
        "polygon": None,
        "parameters": {"NWSheadline": ["Tornado Warning"]},
    },
    "geometry": None,
}

USGS_EVENT_FIXTURE = {
    "id": "us7000test",
    "properties": {
        "mag": 5.2,
        "place": "15km NW of Minneapolis, MN",
        "time": 1746000000000,
        "updated": 1746000060000,
        "alert": "yellow",
        "status": "reviewed",
        "title": "M 5.2 - 15km NW of Minneapolis, MN",
        "type": "earthquake",
        "tsunami": 0,
        "felt": 120,
    },
    "geometry": {"type": "Point", "coordinates": [-93.4, 45.0, 10.0]},
}

def test_normalize_nws_alert():
    result = normalize_nws_alert(NWS_ALERT_FIXTURE)
    assert result["source"] == "nws"
    assert result["hazard_type"] == "tornado_warning"
    assert result["severity"] == "extreme"
    assert result["urgency"] == "immediate"
    assert result["external_id"] == "https://api.weather.gov/alerts/urn:oid:2.49.0.1.840.0.TEST"

def test_normalize_usgs_event():
    result = normalize_usgs_event(USGS_EVENT_FIXTURE)
    assert result["source"] == "usgs"
    assert result["hazard_type"] == "earthquake"
    assert result["severity"] == "moderate"  # mag 5.2 → moderate
    assert result["external_id"] == "us7000test"

def test_nws_deduplicates_external_id():
    a = normalize_nws_alert(NWS_ALERT_FIXTURE)
    b = normalize_nws_alert(NWS_ALERT_FIXTURE)
    assert a["external_id"] == b["external_id"]
