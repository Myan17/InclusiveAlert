# InclusiveAlert — Track A: Real Data Layer (Design Spec)

**Date:** 2026-07-20
**Status:** Approved design → ready for implementation plan
**Scope:** First sub-project of the "real MVP you operate" program. Replaces mock
alert/shelter data with real, live government datasets, and adds an
authority-enrichment layer to fill the accessibility-attribute gap that real
shelter data leaves. This is the honest-data foundation everything else builds on.

---

## 1. Goal

Serve **real, live data** for hazards and shelters, and never fabricate the
accessibility attributes that are InclusiveAlert's differentiator. Where real
data lacks an accessibility fact, the app says "unconfirmed" and lets a verified
authority/EOC account confirm it — data is either **sourced** or **human-verified**,
never guessed.

Responders and victims remain seeded demo accounts in this track (they are real
people, handled in later tracks D/E). This track is data only.

---

## 2. Real data sources (verified live 2026-07-20)

All are free, US-government/NASA, no API key. Ingestion must send a descriptive
`User-Agent` and tolerate outages (log + skip, never crash).

| Source | Endpoint | Provides | Notes |
|---|---|---|---|
| **NWS alerts** | `api.weather.gov/alerts/active?status=actual&message_type=alert` | Weather hazards: severity (extreme/severe/moderate/minor, **lowercase**), certainty, urgency, headline, description, instruction, areaDesc, effective/expires, **GeoJSON polygon** | Already integrated (normalizer exists). Add **polygon ingestion**. |
| **USGS quakes** | `earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson` | Earthquakes; magnitude → severity | Already integrated. |
| **NASA EONET** | `eonet.gsfc.nasa.gov/api/v3/events?category=wildfires&status=open` | Active wildfires: title, point geometry, date | **New.** No severity field → map to `severe` (active wildfire). `external_id` = EONET event id. |
| **FEMA NSS shelters** | `gis.fema.gov/arcgis/rest/services/NSS/FEMA_NSS/MapServer/{0,3}/query` (0=Open, 3=Alert) | shelter_id, name, address, city/state/zip, lat/lon, evacuation_capacity, total_population, `ada_compliant`, `wheelchair_accessible`, `generator_onsite`, `pet_accommodations_desc`, `medical_needs_population`, `self_sufficient_electricity`, floodplain flags, org phone | **New DB sync.** Accessibility fields **exist but are usually blank** (sampled: mostly `" "`, occasionally `"YES"`). **No ASL field.** Only **active-disaster** shelters (~17 open nationally at design time). |

**Consequence (accepted):** between disasters the real shelter feed is nearly
empty. Coverage strategy = **honest + authority-seeded**: authorities pre-register
their own facilities (schools, churches) with accessibility info, so local
coverage always exists and the enrichment model doubles as the seed.

---

## 3. Architecture

- **Ingestion services** (`app/services/`):
  - Extend `alert_ingestion.py`: add EONET wildfire normalizer; parse NWS GeoJSON
    polygons into the existing `hazard_events.geometry` (MULTIPOLYGON) column.
  - New `shelter_ingestion.py`: fetch FEMA NSS (Open + Alert layers) → upsert into
    `shelters`.
- **Scheduler** (existing APScheduler in `main.py`): alerts every 5 min, shelters
  every 30 min. Re-enable ingestion (`enable_live_ingestion` default → **True**;
  keep the env override so demos can turn it off).
- **Tables:** InclusiveAlert's existing `hazard_events` and `shelters`. Every
  state change is written to `audit_events` (already the pattern).

---

## 4. Data model changes

### `shelters` — provenance + tri-state accessibility
The core fix: a boolean `False` currently can't be distinguished from *unknown*.
Change accessibility attributes to **nullable** (`NULL` = unconfirmed).

- Make `wheelchair_accessible`, `ada_compliant`, `generator_onsite`, `asl_support`
  **nullable** (`None` = unconfirmed, `True`/`False` = known). `pet_policy` gains
  an `"unknown"` value.
- Add: `data_source` (`fema_nss` | `authority`; reuse existing `source`),
  `verified_by` (UUID of authority user, nullable), `last_verified_at` (exists),
  `last_synced_at` (nullable), keep `external_id` (= FEMA `shelter_id`).
- `phone` (nullable) ← FEMA `org_main_phone`, for "call to confirm".
- Backfill: existing seeded shelters → accessibility left as-is (already set);
  new FEMA-ingested → blanks become `NULL`.

### `hazard_events`
- Populate `geometry` from NWS polygons (currently always `NULL`).
- Add `wildfire` as an ingested `source` (EONET). `external_id` = EONET id.

---

## 5. Ingestion upsert rules

- Upsert shelters by `external_id` (FEMA `shelter_id`).
- On conflict, always update the **operational** FEMA fields (capacity,
  occupancy, status, location, phone). For **accessibility** fields: if the
  shelter has `verified_by` set (an authority confirmed it), ingestion leaves
  **all** its accessibility attributes untouched; otherwise it refreshes them
  from the feed (blank → `NULL`). Verification is shelter-level, not per-attribute.
  (Human confirmation always wins over a blank feed value.)
- FEMA `"YES"`/`"NO"`/blank → `True`/`False`/`NULL`.
- Shelters absent from the current FEMA feed but previously ingested: mark
  `status = "closed"` rather than delete (preserves history + authority edits).

---

## 6. Authority enrichment

- **`PATCH /shelters/{id}`** (role `authority` only): set/confirm accessibility
  (`wheelchair_accessible`, `ada_compliant`, `generator_onsite`, `asl_support`,
  `pet_policy`, `capacity`, `status`). Sets `verified_by = current_user`,
  `last_verified_at = now`, writes an `audit_events` row.
- **`POST /shelters`** (role `authority` only): pre-register a facility
  (authority-seeded coverage). `data_source = authority`, verified by default.
- **Minimal frontend** (authority role only): a "Manage Shelters" screen — list
  shelters, open one, an accessibility edit form (reusing existing shadcn
  components), save → PATCH. Non-authorities never see it.

---

## 7. Honesty / display rules (frontend)

- Accessibility attribute `True` → show badge (e.g. ♿ Wheelchair, 🧏 ASL).
- `False` → show muted "not wheelchair accessible".
- `NULL` (unconfirmed) → show **"accessibility unconfirmed — call to verify"** with
  the shelter phone; do **not** render a badge.
- Source badge on each shelter: **"FEMA NSS"** or **"Verified by {org}"**.
- **Matching safety:** for a wheelchair/ASL/power-dependent victim, `NULL` is
  treated as *not confirmed accessible* (never routed as if accessible), and
  confirmed-accessible shelters rank above unconfirmed ones. Unknown is displayed
  honestly but never assumed safe.

---

## 8. Out of scope (explicitly deferred to later tracks)

- Responder/victim real onboarding & identity/background verification (Tracks D/E)
- Notifications — SMS/email/voice (Track C)
- Privacy / consent / legal — health-data consent, ToS, waivers (Track F)
- Trust & safety — abuse prevention, reporting, insurance (Track G)
- Production hosting, scaling, monitoring, CI/CD (Track B)
- Full authority moderation console (bulk verify, audit UI)
- Persistent national static shelter list (revisit if authority-seeding proves
  insufficient)

---

## 9. Testing

- **Normalizers** (unit): recorded JSON fixtures for NWS / USGS / EONET / FEMA
  NSS → assert correct `hazard_event` / `shelter` dicts, incl. lowercase severity,
  blank→`NULL` accessibility, polygon parsing. **No live API calls in tests.**
- **Ingestion upsert:** dedup by `external_id`; authority-verified fields are not
  clobbered; disappeared shelters → `closed`.
- **Authority endpoints:** `PATCH`/`POST /shelters` reject non-authority roles;
  provenance + audit rows written.
- **Matching safety:** `NULL` accessibility not treated as accessible; ranking
  order confirmed.
- **Display:** unknown vs known accessibility renders per §7.

---

## 10. Risks

- **Sparse shelter feed between disasters** — mitigated by authority-seeding;
  accepted as the honest real state.
- **External API reliability / rate limits** — all fetches wrapped in try/except,
  logged; a failed poll skips, never crashes ingestion.
- **Nullable-boolean migration** touches existing rows and matching/ranking logic
  — ranking updated to treat `NULL` as "not confirmed accessible" for safety.
- **NWS requires User-Agent** — already handled; keep a real contact string.
