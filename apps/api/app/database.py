# apps/api/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.config import settings


def _async_url(url: str) -> str:
    """Ensure the URL uses the asyncpg driver regardless of how it was provided."""
    return (
        url
        .replace("postgres://", "postgresql+asyncpg://")
        .replace("postgresql://", "postgresql+asyncpg://")
    )


_testing = settings.environment == "testing"
engine = create_async_engine(
    _async_url(settings.database_url),
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
