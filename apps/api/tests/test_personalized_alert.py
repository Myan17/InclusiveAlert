# apps/api/tests/test_personalized_alert.py
"""
Tests for the personalized alert generation service.
"""
from app.services.personalized_alert import generate_alert_message, should_notify


def test_tornado_wheelchair_user():
    """Wheelchair user + tornado warning → accessible transport instruction, sms channel, immediate urgency."""
    user_profile = {
        "disability_needs": ["mobility_wheelchair"],
        "location_zip": "73008",
        "location_state": "OK",
        "service_animal": False,
    }
    hazard = {
        "event_type": "Tornado Warning",
        "area_description": "Central Oklahoma",
        "severity": "Extreme",
        "urgency_level": "Immediate",
        "description": "Large tornado on the ground moving northeast.",
    }
    result = generate_alert_message(user_profile, hazard)

    assert result["urgency"] == "immediate"
    assert "sms" in result["channels"]
    assert any("accessible transportation" in inst for inst in result["instructions"])
    assert any("accessible shelter" in inst for inst in result["instructions"])
    assert "Tornado Warning" in result["subject"]


def test_deaf_flood_warning():
    """Deaf user + flood warning → visual_alert in channels, voice_call NOT in channels, visual alert instruction."""
    user_profile = {
        "disability_needs": ["deaf"],
        "location_zip": "77001",
        "location_state": "TX",
        "service_animal": False,
    }
    hazard = {
        "event_type": "Flash Flood Warning",
        "area_description": "Harris County",
        "severity": "Severe",
        "urgency_level": "Immediate",
        "description": "Flash flooding is occurring.",
    }
    result = generate_alert_message(user_profile, hazard)

    assert "visual_alert" in result["channels"]
    assert "voice_call" not in result["channels"]
    assert any("visual alerts" in inst for inst in result["instructions"])


def test_power_dependent_should_notify_minor():
    """Power-dependent user + Minor severity → should_notify returns True (exception for power-dependent)."""
    user_profile = {
        "disability_needs": ["power_dependent"],
        "location_zip": "30301",
        "location_state": "GA",
        "service_animal": False,
    }
    hazard = {
        "event_type": "Thunderstorm Watch",
        "area_description": "Atlanta Metro",
        "severity": "Minor",
        "urgency_level": "Expected",
        "description": None,
    }
    assert should_notify(user_profile, hazard) is True


def test_no_disability_default_channels():
    """User with no disability needs → channels include both sms and voice_call."""
    user_profile = {
        "disability_needs": [],
        "location_zip": "10001",
        "location_state": "NY",
        "service_animal": False,
    }
    hazard = {
        "event_type": "Severe Thunderstorm Warning",
        "area_description": "Manhattan",
        "severity": "Moderate",
        "urgency_level": "Expected",
        "description": "Strong winds expected.",
    }
    result = generate_alert_message(user_profile, hazard)

    assert "sms" in result["channels"]
    assert "voice_call" in result["channels"]


def test_blind_user_instructions():
    """Blind user + earthquake → trusted-person instruction in list, voice_call in channels."""
    user_profile = {
        "disability_needs": ["blind"],
        "location_zip": "90001",
        "location_state": "CA",
        "service_animal": False,
    }
    hazard = {
        "event_type": "Earthquake",
        "area_description": "Los Angeles County",
        "severity": "Severe",
        "urgency_level": "Immediate",
        "description": "Magnitude 6.2 earthquake detected.",
    }
    result = generate_alert_message(user_profile, hazard)

    assert "voice_call" in result["channels"]
    assert any("trusted person" in inst for inst in result["instructions"])


def test_should_notify_none_severity_not_power_dependent():
    """None severity + no power dependency → should_notify returns False (conservative default)."""
    user_profile = {"disability_needs": ["deaf"], "service_animal": False}
    hazard = {"event_type": "Unknown Event", "severity": None}
    assert should_notify(user_profile, hazard) is False


def test_should_notify_moderate_no_disability():
    """Moderate severity + no disability needs → should_notify returns True."""
    user_profile = {"disability_needs": [], "service_animal": False}
    hazard = {"event_type": "Thunderstorm Warning", "severity": "Moderate"}
    assert should_notify(user_profile, hazard) is True


def test_service_animal_instruction():
    """User with service_animal=True → emergency kit instruction appended."""
    user_profile = {"disability_needs": [], "service_animal": True}
    hazard = {"event_type": "Tornado Warning", "severity": "Extreme", "urgency_level": "Immediate", "area_description": None, "description": None}
    result = generate_alert_message(user_profile, hazard)
    assert any("service animal" in inst for inst in result["instructions"])
