# InclusiveAlert — Deployment Guide

## Architecture
- **Frontend** → Vercel (Next.js)
- **Backend API** → Railway (FastAPI + Python)
- **Database** → Railway PostgreSQL with PostGIS
- **Redis** → Railway Redis (optional — used for caching)

---

## Step 1: Deploy the Backend to Railway

### 1a. Create a Railway account
Go to https://railway.app and sign up (free tier available).

### 1b. Create a new project
1. Click **New Project** → **Deploy from GitHub repo**
2. Connect your GitHub account and select this repo
3. Set the **Root Directory** to `inclusive-alert/apps/api`

### 1c. Add PostgreSQL with PostGIS
1. In your Railway project, click **+ New** → **Database** → **PostgreSQL**
2. After it provisions, click the Postgres service → **Variables** tab
3. Copy the `DATABASE_URL` value — you'll need it

> **Important:** Railway's default Postgres doesn't include PostGIS.
> Use the **PostGIS** template instead:
> Click **+ New** → **Template** → search "PostGIS" → deploy it.

### 1d. Set environment variables in Railway
In your API service → **Variables** tab, add:

| Variable | Value |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` (from Railway Postgres, change `postgresql://` to `postgresql+asyncpg://`) |
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `ENVIRONMENT` | `production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `ALERT_POLL_INTERVAL_SECONDS` | `300` |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` (add after Vercel deploy) |
| `REDIS_URL` | `redis://...` (optional — add Railway Redis if needed) |

### 1e. Deploy
Railway auto-deploys on push. The `railway.toml` runs:
```
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 1f. Get your API URL
After deploy, Railway gives you a URL like:
`https://inclusive-alert-api-production.up.railway.app`

Test it: `curl https://your-api.up.railway.app/health` → `{"status":"ok"}`

---

## Step 2: Deploy the Frontend to Vercel

### 2a. Install Vercel CLI (optional but faster)
```bash
npm install -g vercel
```

### 2b. Deploy via CLI
```bash
cd inclusive-alert/apps/web
vercel
```
When prompted:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name?** → `inclusive-alert`
- **Directory?** → `./` (already in apps/web)
- **Override build settings?** → No

### 2c. OR deploy via Vercel dashboard
1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set **Root Directory** to `inclusive-alert/apps/web`
4. Framework: **Next.js** (auto-detected)

### 2d. Set environment variables in Vercel
In Vercel → Project → **Settings** → **Environment Variables**:

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-api.up.railway.app` |

### 2e. Redeploy
After adding the env var, trigger a redeploy:
```bash
vercel --prod
```
Or push a commit to your main branch.

---

## Step 3: Update CORS on Railway

After you have your Vercel URL (e.g. `https://inclusive-alert.vercel.app`):

1. Go to Railway → API service → Variables
2. Set `ALLOWED_ORIGINS` = `https://inclusive-alert.vercel.app`
3. Railway auto-redeploys

---

## Step 4: Seed demo data on production

```bash
# Update BASE in demo_seed.py to your Railway API URL first
BASE = "https://your-api.up.railway.app"

python3 inclusive-alert/demo_seed.py
```

---

## Quick Deploy Checklist

- [ ] Railway project created with PostGIS database
- [ ] `DATABASE_URL` set in Railway (with `asyncpg` driver)
- [ ] `SECRET_KEY` set in Railway (32+ char random string)
- [ ] `ENVIRONMENT=production` set in Railway
- [ ] API deploys successfully — `/health` returns `{"status":"ok"}`
- [ ] Vercel project created, root dir = `inclusive-alert/apps/web`
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] Frontend deploys — login page loads
- [ ] `ALLOWED_ORIGINS` updated in Railway with Vercel URL
- [ ] Demo seed script run against production API
- [ ] Full login → alerts → shelters → matching → profile flow tested

---

## Troubleshooting

**"Failed to fetch" on Vercel frontend**
→ Check `NEXT_PUBLIC_API_URL` is set correctly in Vercel env vars
→ Check `ALLOWED_ORIGINS` includes your Vercel domain in Railway

**Alembic migration fails on Railway**
→ Ensure `DATABASE_URL` uses `postgresql+asyncpg://` not `postgresql://`
→ Check PostGIS extension is enabled: Railway PostGIS template does this automatically

**PostGIS not available**
→ Use the Railway PostGIS template, not the plain PostgreSQL template
→ Or run: `CREATE EXTENSION IF NOT EXISTS postgis;` in your DB console

**Build fails on Vercel**
→ Ensure root directory is set to `inclusive-alert/apps/web`
→ Check Node version: Vercel uses Node 20 by default (compatible)
