# apps/api/app/main.py
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings
from app.routers import auth, profiles, alerts, shelters, matching
from app.services.alert_ingestion import fetch_and_store_nws_alerts, fetch_and_store_usgs_events

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment != "testing" and settings.enable_live_ingestion:
        scheduler.add_job(
            fetch_and_store_nws_alerts,
            "interval",
            seconds=settings.alert_poll_interval_seconds,
            id="nws_poll",
        )
        scheduler.add_job(
            fetch_and_store_usgs_events,
            "interval",
            seconds=settings.alert_poll_interval_seconds,
            id="usgs_poll",
        )
        scheduler.start()
        # Run once on startup
        await fetch_and_store_nws_alerts()
        await fetch_and_store_usgs_events()
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
