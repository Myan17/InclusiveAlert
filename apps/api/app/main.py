# apps/api/app/main.py
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
import logging
from app.routers import auth, profiles, alerts, shelters, matching
from app.services.alert_ingestion import (
    fetch_and_store_nws_alerts,
    fetch_and_store_usgs_events,
    fetch_and_store_eonet_wildfires,
)
from app.services.shelter_ingestion import fetch_and_store_fema_shelters

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

# (interval_seconds, coroutine, job_id): alerts poll fast, shelters slower.
_ALERT_JOBS = [
    (fetch_and_store_nws_alerts, "nws_poll"),
    (fetch_and_store_usgs_events, "usgs_poll"),
    (fetch_and_store_eonet_wildfires, "eonet_poll"),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment != "testing" and settings.enable_live_ingestion:
        for fn, job_id in _ALERT_JOBS:
            scheduler.add_job(fn, "interval", seconds=settings.alert_poll_interval_seconds, id=job_id)
        scheduler.add_job(fetch_and_store_fema_shelters, "interval", seconds=1800, id="fema_shelters")
        scheduler.start()
        # Run once on startup — never let a slow/failing feed block boot.
        for fn, job_id in _ALERT_JOBS:
            try:
                await fn()
            except Exception:
                logger.exception("startup ingestion failed for %s", job_id)
        try:
            await fetch_and_store_fema_shelters()
        except Exception:
            logger.exception("startup FEMA shelter sync failed")
    yield
    if settings.environment != "testing" and settings.enable_live_ingestion:
        scheduler.shutdown()


app = FastAPI(title="InclusiveAlert API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        # Vercel deployments — set ALLOWED_ORIGINS env var in Railway to add your domain
        *[o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()],
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(alerts.router)
app.include_router(shelters.router)
app.include_router(matching.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
