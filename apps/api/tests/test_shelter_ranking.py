import pytest
from app.services.shelter_ranking import compute_shelter_score, rank_shelters, _accessibility_fit_score


def test_unknown_accessibility_is_not_treated_as_accessible():
    """NULL/None accessibility (unconfirmed real data) must never earn the
    accessible bonus — a wheelchair user is never routed to an unconfirmed
    shelter as if it were accessible. Confirmed-accessible ranks strictly above."""
    needs = {"disability_needs": ["mobility_wheelchair"]}
    confirmed = _accessibility_fit_score({"wheelchair_accessible": True, "ada_compliant": True}, needs)
    unknown = _accessibility_fit_score({"wheelchair_accessible": None, "ada_compliant": None}, needs)
    confirmed_not = _accessibility_fit_score({"wheelchair_accessible": False, "ada_compliant": False}, needs)
    assert confirmed == 1.0
    assert unknown < confirmed        # unconfirmed loses to confirmed-accessible
    assert confirmed_not < confirmed  # confirmed-not also loses to confirmed-accessible

VICTIM_NEEDS = {
    "disability_needs": ["mobility_wheelchair", "power_dependent"],
    "service_animal": True,
}

SHELTER_A = {  # Good accessibility match
    "name": "Shelter A",
    "distance_km": 2.0,
    "wheelchair_accessible": True,
    "ada_compliant": True,
    "generator_onsite": True,
    "pet_policy": "pets_allowed",
    "status": "open",
    "capacity": 200,
    "current_occupancy": 80,
    "hazard_safety_score": 0.9,
    "transport_feasibility": 0.8,
    "last_verified_days_ago": 0,
}

SHELTER_B = {  # Poor accessibility match
    "name": "Shelter B",
    "distance_km": 0.5,
    "wheelchair_accessible": False,
    "ada_compliant": False,
    "generator_onsite": False,
    "pet_policy": "no_pets",
    "status": "open",
    "capacity": 100,
    "current_occupancy": 90,
    "hazard_safety_score": 0.5,
    "transport_feasibility": 0.9,
    "last_verified_days_ago": 30,
}

def test_shelter_score_accessibility_matters():
    score_a = compute_shelter_score(SHELTER_A, VICTIM_NEEDS)
    score_b = compute_shelter_score(SHELTER_B, VICTIM_NEEDS)
    # Shelter A should rank higher despite being farther — accessibility fit is critical
    assert score_a > score_b

def test_shelter_score_range():
    score = compute_shelter_score(SHELTER_A, VICTIM_NEEDS)
    assert 0.0 <= score <= 1.0

def test_rank_shelters_returns_ordered():
    shelters = [SHELTER_B, SHELTER_A]
    ranked = rank_shelters(shelters, VICTIM_NEEDS)
    assert ranked[0]["name"] == "Shelter A"
    assert ranked[0]["shelter_score"] > ranked[1]["shelter_score"]

def test_full_shelter_closed_not_recommended():
    full_shelter = {**SHELTER_A, "status": "full"}
    open_shelter = {**SHELTER_A, "status": "open"}
    ranked = rank_shelters([full_shelter, open_shelter], VICTIM_NEEDS)
    # Full shelter should be penalized below an otherwise identical open shelter
    assert ranked[0]["name"] == "Shelter A" and ranked[0]["status"] == "open"
    assert ranked[0]["shelter_score"] > ranked[1]["shelter_score"]
