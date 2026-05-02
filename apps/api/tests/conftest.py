# apps/api/tests/conftest.py
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.database import Base, get_async_session
from app.main import app as fastapi_app
import app.models  # noqa: F401 — ensures all models are registered

TEST_DB_URL = "postgresql+asyncpg://ia_user:ia_dev_password@localhost:5433/inclusivealert_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(autouse=True)
async def override_db():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async def _get_test_session():
        async with SessionLocal() as session:
            yield session
    fastapi_app.dependency_overrides[get_async_session] = _get_test_session
    yield
    fastapi_app.dependency_overrides.clear()
    await engine.dispose()
