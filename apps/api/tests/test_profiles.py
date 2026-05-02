# apps/api/tests/test_profiles.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def get_token(client, email, role="victim"):
    await client.post("/auth/register", json={"email": email, "password": "Pass123!", "role": role})
    resp = await client.post("/auth/login", data={"username": email, "password": "Pass123!"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_victim_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_token(client, "v1@test.com")
        resp = await client.post("/profiles/victim", json={
            "disability_needs": ["mobility_wheelchair", "power_dependent"],
            "communication_modes": ["text", "haptic"],
            "power_dependency": True,
            "service_animal": False,
            "preferred_language": "en",
            "location_zip": "55401",
            "location_state": "MN",
        }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "mobility_wheelchair" in data["disability_needs"]
    assert data["power_dependency"] is True


@pytest.mark.asyncio
async def test_get_victim_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_token(client, "v2@test.com")
        await client.post("/profiles/victim", json={
            "disability_needs": ["deaf"],
            "communication_modes": ["asl", "text"],
            "preferred_language": "en",
            "location_zip": "55402",
        }, headers={"Authorization": f"Bearer {token}"})
        resp = await client.get("/profiles/victim", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "deaf" in resp.json()["disability_needs"]


@pytest.mark.asyncio
async def test_create_respondent_profile():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        token = await get_token(client, "r1@test.com", role="respondent")
        resp = await client.post("/profiles/respondent", json={
            "skills": ["asl", "cpr"],
            "languages": ["en", "es"],
            "asl_level": "fluent",
            "vehicle_type": "van_wheelchair",
            "vetting_tier": "trained_volunteer",
            "availability_status": "available",
            "max_radius_km": 15.0,
            "location_lat": 44.9778,
            "location_lon": -93.2650,
            "location_zip": "55403",
        }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "asl" in data["skills"]
    assert data["asl_level"] == "fluent"
