# apps/api/tests/test_models.py
import pytest
from sqlalchemy import text
from app.database import get_async_session

EXPECTED_TABLES = [
    "user_profiles",
    "consent_policies",
    "respondent_profiles",
    "hazard_events",
    "shelters",
    "match_assignments",
    "audit_events",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("table", EXPECTED_TABLES)
async def test_table_exists(table):
    async for session in get_async_session():
        result = await session.execute(
            text(
                "SELECT EXISTS ("
                "SELECT FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = :t"
                ")"
            ),
            {"t": table},
        )
        assert result.scalar() is True, f"Table {table} missing"
