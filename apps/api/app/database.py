# apps/api/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings

_testing = settings.environment == "testing"
engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool if _testing else None,
    pool_pre_ping=not _testing,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
