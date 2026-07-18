# InclusiveAlert — Deployment Guide

## Architecture
- **Frontend** → GitHub Pages (Next.js static export) — auto-deployed by GitHub Actions
- **Backend API** → Render (FastAPI in Docker)
- **Database** → Render PostgreSQL (PostGIS enabled by the migration)

The frontend is a fully static site (`output: "export"`) served at
`https://myan17.github.io/InclusiveAlert/`. It talks to the Render backend over
HTTPS using the `NEXT_PUBLIC_API_URL` baked in at build time.

---

## Step 1: Deploy the Backend to Render

### 1a. One-click deploy
Click the button (or open the link) to deploy the `render.yaml` blueprint —
it provisions the FastAPI service **and** a free Postgres database, fully wired:

**https://render.com/deploy?repo=https://github.com/Myan17/InclusiveAlert**

Render reads `render.yaml`, builds `apps/api/Dockerfile`, creates the database,
injects `DATABASE_URL`, and generates a random `SECRET_KEY`. On boot the
container runs `alembic upgrade head` (which enables PostGIS) then starts uvicorn.

### 1b. Grab your API URL
After the service is **Live**, Render shows a URL like
`https://inclusivealert-api.onrender.com`.

Test it: `curl https://<your-api>.onrender.com/health` → `{"status":"ok"}`

> **Free tier note:** the web service sleeps after ~15 min idle; the first
> request after sleeping takes ~50s to cold-start. The free Postgres database
> is retained for 30 days.

### 1c. Seed demo data (optional)
```bash
# Point BASE at your Render URL first, then:
python3 demo_seed.py
```

---

## Step 2: Point the Frontend at your Backend

The GitHub Actions workflow (`.github/workflows/deploy-pages.yml`) builds the
static site with `NEXT_PUBLIC_API_URL`. It defaults to
`https://inclusivealert-api.onrender.com`. If your Render URL differs:

1. Repo → **Settings** → **Secrets and variables** → **Actions** → **Variables**
2. Add a repository **variable** `NEXT_PUBLIC_API_URL` = your Render URL
3. Re-run the workflow (Actions tab → **Deploy frontend to GitHub Pages** →
   **Run workflow**), or push any change under `apps/web/`.

The backend's CORS allow-list already includes `https://myan17.github.io`
(set via `ALLOWED_ORIGINS` in `render.yaml`).

---

## Step 3: Frontend is deployed automatically

GitHub Pages is served from GitHub Actions (no manual build needed). Every push
to `main` that touches `apps/web/**` rebuilds and redeploys the site to:

**https://myan17.github.io/InclusiveAlert/**

Pages must be set to **Source: GitHub Actions** (Settings → Pages). This is
already enabled for this repo.

---

## Deploy Checklist

- [ ] Render blueprint deployed — `/health` returns `{"status":"ok"}`
- [ ] Render API URL noted
- [ ] `NEXT_PUBLIC_API_URL` matches the Render URL (repo variable, if different from default)
- [ ] GitHub Pages source = GitHub Actions
- [ ] Pages workflow is green — site loads at `myan17.github.io/InclusiveAlert/`
- [ ] Login → alerts → shelters → matching → profile flow works end to end

---

## Local development

```bash
# Backend (needs Docker for Postgres/PostGIS)
docker compose up -d db redis
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
export DATABASE_URL=postgresql+asyncpg://ia_user:ia_dev_password@localhost:5432/inclusivealert
export SECRET_KEY=dev-secret-key-change-in-production-min-32-chars
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

---

## Troubleshooting

**"Failed to fetch" on the deployed site**
→ Confirm `NEXT_PUBLIC_API_URL` (repo variable) points at the live Render URL and
  the workflow was re-run after changing it.
→ The Render free service may be cold-starting (~50s on first hit).
→ Confirm `ALLOWED_ORIGINS` on Render includes `https://myan17.github.io`.

**Blank page / 404 for assets on GitHub Pages**
→ The site lives under the `/InclusiveAlert` sub-path; the build sets
  `NEXT_PUBLIC_BASE_PATH=/InclusiveAlert`. Don't open asset URLs without that prefix.

**Alembic migration fails on Render**
→ `DATABASE_URL` is injected from the Render database automatically;
  `app/database.py` rewrites the scheme to `postgresql+asyncpg://`.
→ PostGIS is created by the initial migration; if unavailable the schema still
  builds (geometry columns degrade gracefully).
