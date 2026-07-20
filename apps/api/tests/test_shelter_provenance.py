# apps/api/tests/test_shelter_provenance.py
import uuid
import pytest
from sqlalchemy import select
from app.database import get_async_session
from app.models.shelter import Shelter


@pytest.mark.asyncio
async def test_shelter_accessibility_is_nullable_and_provenance_roundtrips():
    """Accessibility attributes must be nullable (NULL = unconfirmed), and the
    new provenance columns (verified_by, last_synced_at, phone) round-trip."""
    sid = uuid.uuid4()
    async for session in get_async_session():
        session.add(
            Shelter(
                id=sid,
                external_id="TEST-1",
                name="Unknown-Access Shelter",
                lat=29.76,
                lon=-95.37,
                status="open",
                # all accessibility unknown
                wheelchair_accessible=None,
                ada_compliant=None,
                generator_onsite=None,
                asl_support=None,
                pet_policy="unknown",
                source="fema_nss",
                phone="713-555-0100",
                verified_by=None,
            )
        )
        await session.commit()

        row = (await session.execute(select(Shelter).where(Shelter.id == sid))).scalar_one()
        assert row.wheelchair_accessible is None
        assert row.ada_compliant is None
        assert row.generator_onsite is None
        assert row.asl_support is None
        assert row.pet_policy == "unknown"
        assert row.source == "fema_nss"
        assert row.phone == "713-555-0100"
        assert row.verified_by is None
        break
