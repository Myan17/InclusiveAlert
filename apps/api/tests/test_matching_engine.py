# apps/api/tests/test_matching_engine.py
"""
Tests for the matching engine (MatchScore formula) and /matching/assign endpoint.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.matching_engine import compute_match_score, rank_respondents


# ---------------------------------------------------------------------------
# Unit tests — pure scoring functions
# ---------------------------------------------------------------------------

def test_compute_match_score_perfect():
    """
    Wheelchair victim + nearby mobility_assistant respondent who is available,
    trust_tier=5, has asl communication mode → score should be near 1.0.
    """
    victim = {
        "lat": 40.0,
        "lon": -75.0,
        "disability_needs": ["mobility_wheelchair", "deaf"],
    }
    respondent = {
        "respondent_id": "resp-001",
        "lat": 40.001,   # very close (~0.1 km)
        "lon": -75.001,
        "skills": ["mobility_assistant", "asl_interpreter"],
        "availability_status": "available",
        "trust_tier": 5,
        "communication_modes": ["asl", "text", "voice"],
    }
    result = compute_match_score(victim, respondent)

    assert result["respondent_id"] == "resp-001"
    assert result["score"] >= 0.85, f"Expected near-perfect score, got {result['score']}"
    assert 0.0 <= result["score"] <= 1.0

    bd = result["breakdown"]
    assert bd["proximity"] > 0.99   # basically at same location
    assert bd["skill_fit"] == 1.0   # both needs covered
    assert bd["availability"] == 1.0
    assert bd["route_safety"] == 0.5  # always placeholder
    assert bd["trust_tier"] == 1.0   # tier 5 → (5-1)/4 = 1.0
    assert bd["communication_fit"] == 1.0  # deaf → asl covered


def test_compute_match_score_unavailable_respondent():
    """
    An unavailable respondent should have availability component = 0.0.
    """
    victim = {
        "lat": 40.0,
        "lon": -75.0,
        "disability_needs": ["mobility_wheelchair"],
    }
    respondent = {
        "respondent_id": "resp-002",
        "lat": 40.0,
        "lon": -75.0,
        "skills": ["mobility_assistant"],
        "availability_status": "unavailable",
        "trust_tier": 3,
        "communication_modes": [],
    }
    result = compute_match_score(victim, respondent)

    assert result["breakdown"]["availability"] == 0.0
    # Score should still be bounded [0, 1]
    assert 0.0 <= result["score"] <= 1.0


def test_skill_fit_no_match():
    """
    Victim needs deaf + power_dependent, respondent only has 'cooking' skill → skill_fit = 0.0.
    """
    victim = {
        "lat": 40.0,
        "lon": -75.0,
        "disability_needs": ["deaf", "power_dependent"],
    }
    respondent = {
        "respondent_id": "resp-003",
        "lat": 40.0,
        "lon": -75.0,
        "skills": ["cooking"],
        "availability_status": "available",
        "trust_tier": 2,
        "communication_modes": [],
    }
    result = compute_match_score(victim, respondent)

    assert result["breakdown"]["skill_fit"] == 0.0


def test_rank_respondents_ordering():
    """
    3 respondents with different characteristics → verify sorted descending by score.
    """
    victim = {
        "lat": 40.0,
        "lon": -75.0,
        "disability_needs": ["mobility_wheelchair"],
    }

    # Best: close, skilled, available, high trust
    best = {
        "respondent_id": "best",
        "lat": 40.001,
        "lon": -75.001,
        "skills": ["mobility_assistant"],
        "availability_status": "available",
        "trust_tier": 5,
        "communication_modes": [],
    }
    # Middle: farther, on break, medium trust
    middle = {
        "respondent_id": "middle",
        "lat": 40.5,
        "lon": -75.5,
        "skills": ["mobility_assistant"],
        "availability_status": "on_break",
        "trust_tier": 3,
        "communication_modes": [],
    }
    # Worst: no location, unavailable, no skills
    worst = {
        "respondent_id": "worst",
        "lat": None,
        "lon": None,
        "skills": [],
        "availability_status": "unavailable",
        "trust_tier": 1,
        "communication_modes": [],
    }

    ranked = rank_respondents(victim, [worst, middle, best])

    assert len(ranked) == 3
    assert ranked[0]["respondent_id"] == "best"
    assert ranked[1]["respondent_id"] == "middle"
    assert ranked[2]["respondent_id"] == "worst"
    assert ranked[0]["score"] > ranked[1]["score"] > ranked[2]["score"]


# ---------------------------------------------------------------------------
# HTTP endpoint test
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_matching_endpoint(override_db):
    """
    Register + login a victim user, then call GET /matching/assign?lat=40.0&lon=-75.0.
    Assert 200 response with 'results' key.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register a victim user
        reg_resp = await client.post("/auth/register", json={
            "email": "match_victim@test.com",
            "password": "SecurePass123!",
            "role": "victim",
        })
        assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"

        # Login to get token
        login_resp = await client.post("/auth/login", data={
            "username": "match_victim@test.com",
            "password": "SecurePass123!",
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        token = login_resp.json()["access_token"]

        # Call the matching endpoint
        resp = await client.get(
            "/matching/assign?lat=40.0&lon=-75.0",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "results" in data, f"'results' key missing from response: {data}"
    assert "total" in data
    assert isinstance(data["results"], list)
