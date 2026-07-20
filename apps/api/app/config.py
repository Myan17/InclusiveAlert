# apps/api/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    access_token_expire_minutes: int = 60
    alert_poll_interval_seconds: int = 60
    environment: str = "development"
    # When false (the default), the NWS/USGS live ingestion scheduler is disabled
    # so the app serves only the curated demo alerts. Set ENABLE_LIVE_INGESTION=true
    # to poll live feeds. Defaulting off keeps the demo curated without relying on
    # a blueprint-managed env var being present.
    enable_live_ingestion: bool = False


settings = Settings()
