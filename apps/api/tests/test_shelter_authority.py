# apps/api/tests/test_shelter_authority.py
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def get_token(client, email, role):
    await client.post("/auth/register", json={"email": email, "password": "Pass123!", "role": role})
    r = await client.post("/auth/login", data={"username": email, "password": "Pass123!"})
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_authority_can_create_and_verify_shelter():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        atok = await get_token(client, "auth1@test.com", "authority")
        # 1. Authority seeds a facility
        r = await client.post(
            "/shelters",
            json={
                "name": "Lincoln High School", "lat": 29.76, "lon": -95.37, "address": "1 Main St",
                "capacity": 400, "wheelchair_accessible": True, "asl_support": True,
                "pet_policy": "service_animals_only",
            },
            headers={"Authorization": f"Bearer {atok}"},
        )
        assert r.status_code == 201, r.text
        body = r.json()
        sid = body["id"]
        assert body["source"] == "authority"
        assert body["wheelchair_accessible"] is True
        assert body["verified_by"] is not None

        # 2. Authority confirms/changes accessibility
        r2 = await client.patch(
            f"/shelters/{sid}",
            json={"generator_onsite": True, "asl_support": False},
            headers={"Authorization": f"Bearer {atok}"},
        )
        assert r2.status_code == 200, r2.text
        assert r2.json()["generator_onsite"] is True
        assert r2.json()["asl_support"] is False
        assert r2.json()["verified_by"] is not None


@pytest.mark.asyncio
async def test_non_authority_cannot_create_or_patch():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        vtok = await get_token(client, "vic1@test.com", "victim")
        r = await client.post(
            "/shelters", json={"name": "X", "lat": 1.0, "lon": 1.0},
            headers={"Authorization": f"Bearer {vtok}"},
        )
        assert r.status_code == 403
        r2 = await client.patch(
            f"/shelters/{uuid.uuid4()}", json={"wheelchair_accessible": True},
            headers={"Authorization": f"Bearer {vtok}"},
        )
        assert r2.status_code == 403


@pytest.mark.asyncio
async def test_patch_missing_shelter_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        atok = await get_token(client, "auth2@test.com", "authority")
        r = await client.patch(
            f"/shelters/{uuid.uuid4()}", json={"wheelchair_accessible": True},
            headers={"Authorization": f"Bearer {atok}"},
        )
        assert r.status_code == 404
