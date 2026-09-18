# InclusiveAlert

Disaster alerting and responder matching for people with disabilities — built on
real government hazard feeds, with accessibility facts that are **either sourced
or human-verified, never guessed**.

[![CI](https://github.com/Myan17/InclusiveAlert/actions/workflows/ci.yml/badge.svg)](https://github.com/Myan17/InclusiveAlert/actions/workflows/ci.yml)
[![Pages](https://github.com/Myan17/InclusiveAlert/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/Myan17/InclusiveAlert/actions/workflows/deploy-pages.yml)

**Live frontend:** https://myan17.github.io/InclusiveAlert/

---

## The problem

Emergency alerts are broadcast identically to everyone. A wheelchair user, a Deaf
resident, and someone on a home ventilator each need a different instruction from
the same hazard — and each needs a different shelter. Public shelter data makes
this worse: FEMA's National Shelter System *has* accessibility columns
(`ada_compliant`, `wheelchair_accessible`, `generator_onsite`), and in practice
they are almost always blank.

InclusiveAlert's position on that gap is the core design decision: **it never
fabricates an accessibility attribute.** A shelter's accessibility is either
sourced from the feed, confirmed by a verified authority/EOC account, or displayed
as `unconfirmed`. Provenance is recorded per attribute and enforced by tests
(`test_shelter_provenance.py`, `test_shelter_authority.py`).

## What it does

- **Ingests live hazards** — NWS active alerts (with GeoJSON polygons), USGS
  earthquakes, NASA EONET wildfires. No API keys; ingestion tolerates outages by
  logging and skipping rather than crashing.
- **Ingests real shelters** — FEMA NSS Open and Alert layers, upserted on a
  30-minute schedule.
- **Geofences** hazards against user location using PostGIS geography columns.
- **Personalizes the alert text** per disability profile, rather than broadcasting
  one message.
- **Ranks shelters** by distance and by accessibility fit against the user's
  declared needs.
- **Matches responders to victims** with a weighted score
  (`app/services/matching_engine.py`): 25% proximity, 25% skill fit, 15%
  availability, 15% route safety, 10% trust tier, 10% communication fit. Route
  safety is currently a fixed 0.5 placeholder — there is no live routing data, and
  the code says so rather than inventing a number.
- **Audits every state change** into an `audit_events` table.

## Architecture

```
Next.js static export ──► GitHub Pages (live)
        │  NEXT_PUBLIC_API_URL baked in at build
        ▼
FastAPI + APScheduler ──► Render (Docker)
        │
        ▼
PostgreSQL + PostGIS   ◄── alembic migrations (enable PostGIS on boot)
        ▲
        └── ingestion: NWS · USGS · NASA EONET · FEMA NSS
```

| Layer | Stack |
|---|---|
| Frontend | Next.js (static export), TypeScript, Tailwind, Zustand |
| API | FastAPI, SQLAlchemy 2 async, Pydantic v2, APScheduler |
| Database | PostgreSQL 16 + PostGIS 3.4, Alembic migrations |
| Auth | JWT (python-jose), bcrypt |

## Testing

61 tests run on every push: 55 pytest cases against a real PostGIS service
container (not a mock — the geofence and ranking logic is SQL-level), plus 6
Jest cases on the frontend, with `tsc --noEmit` and a production `next build`.

| Suite | Cases | Covers |
|---|---|---|
| `test_alert_ingestion.py` | 9 | NWS/USGS/EONET normalizers, outage tolerance |
| `test_personalized_alert.py` | 8 | per-disability message generation |
| `test_matching_engine.py` | 5 | responder scoring weights |
| `test_shelter_ranking.py` | 5 | distance + accessibility-fit ranking |
| `test_smoke.py` | 5 | app boot, health, router wiring |
| `test_shelter_ingestion.py` | 4 | FEMA NSS upsert |
| `test_shelter_authority.py` | 4 | authority confirmation of attributes |
| `test_geofence.py` | 4 | PostGIS containment + distance |
| `test_auth.py` | 4 | JWT issue/verify, password hashing |
| `test_profiles.py` | 3 | disability profile CRUD |
| `test_database.py` / `test_models.py` / `test_shelter_provenance.py` | 4 | schema, provenance invariants |
| `apps/web/__tests__` | 6 | API client, auth store |

Coverage is gated at 60% in CI; the run fails below that line.

```bash
# API — needs the compose Postgres up on 5433
docker compose up -d db
cd apps/api && pip install -e ".[dev]" && pytest --cov=app

# Web
cd apps/web && npm ci && npm test
```

## Running locally

```bash
cp .env.example .env          # set SECRET_KEY to 32+ random chars
docker compose up -d          # postgis + redis + api on :8000
python3 seed.py               # demo users and profiles
python3 seed_shelters.py      # shelter fixtures
cd apps/web && npm ci && npm run dev   # frontend on :3000
```

## Deployment

See [DEPLOY.md](DEPLOY.md). The frontend deploys to GitHub Pages automatically on
push to `apps/web/**`. The backend deploys from `render.yaml` as a Docker service
with a managed Postgres; `alembic upgrade head` runs on boot to enable PostGIS.

> **Current status:** the Render free-tier backend is not running, so the live
> frontend has no API behind it. Redeploy from the blueprint in DEPLOY.md, then
> set the `NEXT_PUBLIC_API_URL` Actions variable to the new URL.

## Known limitations

- Route safety in the matching engine is a fixed placeholder; there is no live
  routing integration.
- The FEMA NSS feed only lists shelters during active disasters — roughly 17 open
  nationally at design time. Between disasters, coverage depends on
  authority-registered facilities.
- Responder and victim accounts are seeded demo accounts; real-user onboarding is
  not built.
- There is no ASL-interpreter field in any public shelter feed; that attribute can
  only ever come from authority verification.
