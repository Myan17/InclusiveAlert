# Real Data Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or subagent-driven-development to implement task-by-task. Steps use `- [ ]`.

**Goal:** Replace mock alerts/shelters with real government feeds (NWS/USGS/EONET, FEMA NSS) and add an authority-enrichment layer for accessibility attributes.

**Architecture:** Extend the existing APScheduler ingestion in `app/services`; add a FEMA-NSS→DB shelter sync; make shelter accessibility nullable (NULL=unconfirmed); add authority-only endpoints to confirm/seed shelters; keep display + matching honest about unknowns.

**Tech Stack:** Python 3.12 · FastAPI · SQLAlchemy async · asyncpg · Alembic · APScheduler · httpx · PostGIS/geoalchemy2 · shapely · Next.js 16 frontend.

## Global Constraints
- Python `requires-python >=3.12`; FastAPI; SQLAlchemy async + asyncpg.
- All external fetches wrapped in try/except → log + skip, never crash ingestion.
- NWS calls MUST send a descriptive `User-Agent`.
- Tests never hit live APIs — use recorded JSON fixtures.
- Accessibility unknown is `NULL`, never guessed; matching treats `NULL` as "not confirmed accessible".
- Every state change already writes to `audit_events` where that pattern exists.

---

### Task 1: Shelter model — nullable accessibility + provenance (migration)
**Files:** Modify `apps/api/app/models/shelter.py`; Modify `apps/api/app/schemas/shelter.py`; Create `apps/api/alembic/versions/<rev>_shelter_provenance.py`; Test `apps/api/tests/test_shelter_provenance.py`
**Interfaces — Produces:** `Shelter` with nullable `wheelchair_accessible/ada_compliant/generator_onsite/asl_support: bool|None`, `pet_policy` allows `"unknown"`, new `verified_by: UUID|None`, `last_synced_at: datetime|None`, `phone: str|None`. `ShelterResponse` returns these + `source`.

- [ ] Test: creating a Shelter with all accessibility = None persists and reads back None; `source`/`verified_by` round-trip.
- [ ] Make the 4 accessibility bool columns `nullable=True` (drop the `default=False`); add `verified_by (UUID, nullable)`, `last_synced_at (DateTime tz, nullable)`, `phone (String, nullable)`.
- [ ] Alembic migration: `alter_column` the 4 bools to nullable; `add_column` verified_by/last_synced_at/phone. Down-rev = current head. Idempotent guards like the existing lat/lon migration.
- [ ] Update `ShelterResponse` schema: accessibility fields `Optional[bool]`, add `source`, `verified_by`, `phone`.
- [ ] Run migration on the test DB; run the test; commit.

### Task 2: EONET wildfire ingestion
**Files:** Modify `apps/api/app/services/alert_ingestion.py`; Test `apps/api/tests/test_alert_ingestion.py`; Fixture `apps/api/tests/fixtures/eonet_wildfires.json`
**Interfaces — Consumes:** `_upsert_event(db, data)`. **Produces:** `normalize_eonet_event(feature: dict) -> dict`, `fetch_and_store_eonet_wildfires() -> int`.

- [ ] Save a trimmed real EONET response as the fixture (2-3 events).
- [ ] Test: `normalize_eonet_event` maps title→headline, `hazard_type="wildfire"`, `severity="severe"`, `source="eonet"`, `external_id=<id>`, point geometry → `geometry_wkt` (POINT wkt), effective_at from date.
- [ ] Implement `normalize_eonet_event` + `fetch_and_store_eonet_wildfires` (httpx GET, try/except→0, upsert loop, single commit) mirroring the USGS function.
- [ ] Test passes; commit.

### Task 3: NWS polygon geometry ingestion
**Files:** Modify `apps/api/app/services/alert_ingestion.py`; Test `apps/api/tests/test_alert_ingestion.py`; Fixture `apps/api/tests/fixtures/nws_polygon_alert.json`
**Interfaces — Modifies:** `normalize_nws_alert` now sets `geometry_wkt` from GeoJSON Polygon/MultiPolygon; `_upsert_event` already converts `geometry_wkt`→PostGIS.

- [ ] Fixture: one NWS feature with a Polygon geometry.
- [ ] Test: `normalize_nws_alert` produces a MULTIPOLYGON WKT (wrap Polygon as single-poly MultiPolygon) when geometry present; `None` when absent.
- [ ] Implement GeoJSON→WKT via shapely (`shapely.geometry.shape` + `.wkt`, coerce Polygon→MultiPolygon).
- [ ] Test passes; commit.

### Task 4: FEMA NSS shelter ingestion (normalizer + upsert)
**Files:** Create `apps/api/app/services/shelter_ingestion.py`; Test `apps/api/tests/test_shelter_ingestion.py`; Fixture `apps/api/tests/fixtures/fema_nss_shelters.json`
**Interfaces — Produces:** `normalize_fema_shelter(attrs: dict) -> dict`, `fetch_and_store_fema_shelters() -> int`, `_upsert_shelter(db, data)`.

- [ ] Fixture: FEMA NSS ArcGIS `features` array with mixed accessibility (`"YES"`, blank `" "`, `"NO"`), capacity, lat/lon, org phone.
- [ ] Test: `normalize_fema_shelter` maps `"YES"→True`, `"NO"→False`, blank→`None`; `external_id=shelter_id`; `source="fema_nss"`; location from lat/lon; `phone` from org_main_phone; `asl_support=None` (never in feed).
- [ ] Test: `_upsert_shelter` inserts new by `external_id`; on conflict updates operational fields; if existing row has `verified_by` set, accessibility fields are NOT overwritten.
- [ ] Implement normalizer + fetch (Open layer 0 + Alert layer 3, try/except→0) + upsert (ST_SetSRID/ST_MakePoint via geoalchemy2 from_shape, or raw). Commit once per fetch.
- [ ] Tests pass; commit.

### Task 5: Wire ingestion into scheduler + re-enable
**Files:** Modify `apps/api/app/main.py`; Modify `apps/api/app/config.py`; Modify `render.yaml`
**Interfaces:** none new.

- [ ] `config.py`: `enable_live_ingestion: bool = True` (real MVP default on).
- [ ] `main.py` lifespan: add scheduler jobs for `fetch_and_store_eonet_wildfires` (5 min) and `fetch_and_store_fema_shelters` (30 min); run all once on startup.
- [ ] `render.yaml`: no ENABLE_LIVE_INGESTION needed (default true) — leave as-is.
- [ ] Manual verify: boot container against test DB, confirm scheduler starts, `/alerts/active` + `/shelters/ranked` return live-shaped data; commit.

### Task 6: Authority enrichment endpoints
**Files:** Modify `apps/api/app/routers/shelters.py`; Create `apps/api/app/schemas/shelter.py` additions (`ShelterUpdate`, `ShelterCreate`); Test `apps/api/tests/test_shelter_authority.py`
**Interfaces — Produces:** `PATCH /shelters/{id}` and `POST /shelters`, both role=`authority` only.

- [ ] Test: non-authority PATCH/POST → 403; authority PATCH sets accessibility + `verified_by`/`last_verified_at`, writes audit row; POST creates `source="authority"` shelter.
- [ ] `ShelterUpdate` (all optional accessibility fields + capacity/status); `ShelterCreate` (name, lat, lon, address, capacity, accessibility).
- [ ] Implement endpoints with `Depends(get_current_user)` + role check; audit via existing `audit_events` model.
- [ ] Tests pass; commit.

### Task 7: Matching/display honesty (backend)
**Files:** Modify `apps/api/app/routers/shelters.py` (ranked payload) and `apps/api/app/services/shelter_ranking.py`; Test `apps/api/tests/test_shelter_ranking.py`
**Interfaces:** ranked shelter dicts include `source`, `verified_by`, `phone`, and accessibility as `bool|None`.

- [ ] Test: `_accessibility_fit_score` treats `None` (unknown) as NOT accessible for wheelchair/power needs (no bonus), and a confirmed-accessible shelter ranks above an unknown one for a wheelchair victim.
- [ ] Update ranking to use `is True`/`is not True` semantics (None ≠ accessible); include provenance in the router payload dicts.
- [ ] Tests pass; commit.

### Task 8: Frontend — honest shelter display
**Files:** Modify `apps/web/lib/types.ts` (nullable accessibility + source/phone); Modify `apps/web/components/shelters/ShelterCard.tsx` and `apps/web/components/map/ShelterLayer.tsx`
**Interfaces:** `Shelter` type accessibility fields `boolean | null`; add `source`, `phone`.

- [ ] Update `Shelter` TS type; badges render only when `=== true`; `=== null` renders "Accessibility unconfirmed — call to verify" + phone; source badge ("FEMA NSS" / "Verified").
- [ ] `npm run build` + `npm test` green; commit.

### Task 9: Frontend — authority Manage Shelters screen
**Files:** Create `apps/web/app/dashboard/manage-shelters/page.tsx`; Modify `apps/web/lib/api.ts` (patchShelter, createShelter); Modify `apps/web/components/layout/Sidebar.tsx` (authority-only link)
**Interfaces — Consumes:** `api.shelters.patch/create`.

- [ ] `api.ts`: `shelters.patch(token,id,data)` → PATCH; `shelters.create(token,data)` → POST.
- [ ] Authority-only page: list shelters, select one, accessibility edit form (shadcn), save→patch; "Add facility" form→create. Sidebar link shown only when `role==="authority"`.
- [ ] `npm run build` green; commit.

## Self-Review notes
- Spec §2 sources → Tasks 2,3,4. §4 model → Task 1. §5 upsert rules → Task 4. §6 enrichment → Tasks 6,9. §7 honesty → Tasks 7,8. §9 testing → per-task tests. All covered.
