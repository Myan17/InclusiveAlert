# apps/api/tests/test_shelter_ingestion.py
import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.models.shelter import Shelter
from app.services.shelter_ingestion import normalize_fema_shelter, _upsert_shelter

TEST_DB_URL = "postgresql+asyncpg://ia_user:ia_dev_password@localhost:5433/inclusivealert_test"


def _attrs(**over):
    base = {
        "shelter_id": "FEMA-1",
        "shelter_name": "Accessible High School",
        "address_1": "1 Main",
        "city": "Houston",
        "state": "TX",
        "zip": "77002",
        "evacuation_capacity": 500,
        "total_population": 10,
        "ada_compliant": "YES",
        "wheelchair_accessible": "YES",
        "generator_onsite": "NO",
        "pet_accommodations_desc": "Service animals only",
        "latitude": 29.76,
        "longitude": -95.37,
        "org_main_phone": "713-555-0100",
        "shelter_status_code": "OPEN",
    }
    base.update(over)
    return base


def test_normalize_fema_maps_yes_no_blank():
    r = normalize_fema_shelter(_attrs())
    assert r["external_id"] == "FEMA-1"
    assert r["source"] == "fema_nss"
    assert r["wheelchair_accessible"] is True
    assert r["ada_compliant"] is True
    assert r["generator_onsite"] is False        # "NO" → False
    assert r["asl_support"] is None              # never in the feed
    assert r["phone"] == "713-555-0100"
    assert r["lat"] == 29.76 and r["lon"] == -95.37
    assert r["capacity"] == 500

    unknown = normalize_fema_shelter(_attrs(wheelchair_accessible="UNK", ada_compliant=" "))
    assert unknown["wheelchair_accessible"] is None   # "UNK" → None
    assert unknown["ada_compliant"] is None           # blank → None


def test_normalize_fema_pet_policy_and_status():
    assert normalize_fema_shelter(_attrs(pet_accommodations_desc="Service animals only"))["pet_policy"] == "service_animals_only"
    assert normalize_fema_shelter(_attrs(pet_accommodations_desc="Pets welcome"))["pet_policy"] == "pets_allowed"
    assert normalize_fema_shelter(_attrs(pet_accommodations_desc=" "))["pet_policy"] == "unknown"
    assert normalize_fema_shelter(_attrs(shelter_status_code="CLOSED"))["status"] == "closed"


@pytest.mark.asyncio
async def test_upsert_inserts_then_updates_by_external_id():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    SL = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    eid = f"FEMA-{uuid.uuid4()}"
    async with SL() as s:
        await _upsert_shelter(s, normalize_fema_shelter(_attrs(shelter_id=eid, evacuation_capacity=100)))
        await s.commit()
        await _upsert_shelter(s, normalize_fema_shelter(_attrs(shelter_id=eid, evacuation_capacity=250)))
        await s.commit()
        rows = (await s.execute(select(Shelter).where(Shelter.external_id == eid))).scalars().all()
    await engine.dispose()
    assert len(rows) == 1                  # upsert, not duplicate
    assert rows[0].capacity == 250         # operational field refreshed


@pytest.mark.asyncio
async def test_upsert_never_overwrites_authority_verified_accessibility():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    SL = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    eid = f"FEMA-{uuid.uuid4()}"
    async with SL() as s:
        # Authority-verified shelter: wheelchair confirmed True
        s.add(Shelter(id=uuid.uuid4(), external_id=eid, name="Verified", lat=29.7, lon=-95.3,
                      status="open", wheelchair_accessible=True, source="fema_nss",
                      verified_by=uuid.uuid4()))
        await s.commit()
        # FEMA feed says wheelchair unknown (None) → must NOT clobber the human value
        await _upsert_shelter(s, normalize_fema_shelter(_attrs(shelter_id=eid, wheelchair_accessible="UNK", evacuation_capacity=999)))
        await s.commit()
        row = (await s.execute(select(Shelter).where(Shelter.external_id == eid))).scalar_one()
    await engine.dispose()
    assert row.wheelchair_accessible is True   # authority value preserved
    assert row.capacity == 999                 # operational field still refreshed
