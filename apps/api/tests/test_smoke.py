# apps/api/tests/test_smoke.py
"""
End-to-end smoke tests for all API endpoints.
Uses AsyncClient + ASGITransport (in-process ASGI, no real network).
The conftest.py handles DB setup and dependency override automatically.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE = "http://test"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE) as c:
        yield c


@pytest.fixture
async def auth_client(client):
    """Registers a test user, logs in, returns (client, token)."""
    email = "smoke_test@example.com"
    password = "SmokeTest123!"
    await client.post("/auth/register", json={"email": email, "password": password, "role": "victim"})
    resp = await client.post("/auth/login", data={"username": email, "password": password})
    token = resp.json()["access_token"]
    return client, token


# ---------------------------------------------------------------------------
# 1. Health endpoint
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_endpoint(client):
    """GET /health → 200, body {"status": "ok"}"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# 2. Register and login happy path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_and_login(client):
    """POST /auth/register → 201; POST /auth/login → 200 with access_token."""
    reg_resp = await client.post(
        "/auth/register",
        json={"email": "newuser@smoke.com", "password": "Secure123!", "role": "victim"},
    )
    assert reg_resp.status_code == 201, f"Register failed: {reg_resp.text}"

    login_resp = await client.post(
        "/auth/login",
        data={"username": "newuser@smoke.com", "password": "Secure123!"},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    data = login_resp.json()
    assert "access_token" in data, f"'access_token' key missing: {data}"


# ---------------------------------------------------------------------------
# 3. Auth-required endpoints reject unauthenticated requests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_auth_required_endpoints_reject_without_token(client):
    """
    GET /profiles/victim, GET /shelters/ranked, GET /matching/assign
    with no Authorization header → all return 401.
    """
    victim_resp = await client.get("/profiles/victim")
    assert victim_resp.status_code == 401, (
        f"Expected 401 for /profiles/victim, got {victim_resp.status_code}"
    )

    shelters_resp = await client.get("/shelters/ranked?lat=40&lon=-75")
    assert shelters_resp.status_code == 401, (
        f"Expected 401 for /shelters/ranked, got {shelters_resp.status_code}"
    )

    matching_resp = await client.get("/matching/assign?lat=40&lon=-75")
    assert matching_resp.status_code == 401, (
        f"Expected 401 for /matching/assign, got {matching_resp.status_code}"
    )


# ---------------------------------------------------------------------------
# 4. Full profile flow: register → login → update profile → get profile
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_profile_flow(auth_client):
    """
    Register → Login → POST /profiles/victim (with disability_needs + location)
    → GET /profiles/victim → assert profile was saved correctly.
    """
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}

    update_resp = await client.post(
        "/profiles/victim",
        json={
            "disability_needs": ["deaf", "mobility_wheelchair"],
            "location_zip": "10001",
            "location_state": "NY",
            "location_city": "New York",
        },
        headers=headers,
    )
    assert update_resp.status_code == 200, f"Profile update failed: {update_resp.text}"

    get_resp = await client.get("/profiles/victim", headers=headers)
    assert get_resp.status_code == 200, f"Profile GET failed: {get_resp.text}"
    profile = get_resp.json()
    assert "deaf" in profile["disability_needs"], f"Expected 'deaf' in disability_needs: {profile}"
    assert "mobility_wheelchair" in profile["disability_needs"]
    assert profile["location_zip"] == "10001"
    assert profile["location_state"] == "NY"


# ---------------------------------------------------------------------------
# 5. Alerts endpoint returns a list (may be empty in test env)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_alerts_endpoint_returns_list(auth_client):
    """
    Register → Login → GET /alerts/active (with Authorization)
    → 200, response is a list (may be empty, we just verify the shape).
    """
    client, token = auth_client
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/alerts/active", headers=headers)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, list), f"Expected list response, got {type(data)}: {data}"
