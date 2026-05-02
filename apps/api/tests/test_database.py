# apps/api/tests/test_database.py
import pytest
from sqlalchemy import text
from app.database import get_async_session

@pytest.mark.asyncio
async def test_database_connection():
    async for session in get_async_session():
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_postgis_extension():
    async for session in get_async_session():
        result = await session.execute(text("SELECT PostGIS_Version()"))
        version = result.scalar()
        assert version is not None
