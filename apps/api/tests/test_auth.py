# apps/api/tests/test_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_register_victim():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/register", json={
            "email": "victim@test.com",
            "password": "SecurePass123!",
            "role": "victim"
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "victim@test.com"
    assert data["role"] == "victim"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_returns_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "logintest@test.com",
            "password": "SecurePass123!",
            "role": "victim"
        })
        resp = await client.post("/auth/login", data={
            "username": "logintest@test.com",
            "password": "SecurePass123!"
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_me_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/auth/me")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_me_returns_current_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/auth/register", json={
            "email": "metest@test.com", "password": "SecurePass123!", "role": "respondent"
        })
        login = await client.post("/auth/login", data={
            "username": "metest@test.com", "password": "SecurePass123!"
        })
        token = login.json()["access_token"]
        resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "metest@test.com"
