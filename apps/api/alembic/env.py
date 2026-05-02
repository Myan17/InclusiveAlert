# apps/api/alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context
from app.config import settings
from app.database import Base
import app.models  # noqa: F401 — registers all models with Base.metadata

config = context.config

# Convert asyncpg URL to psycopg2 for alembic's sync migration runner
# asyncpg is used by the app at runtime; psycopg2 is used only by alembic
def _make_sync_url(url: str) -> str:
    return (
        url
        .replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        .replace("postgres+asyncpg://", "postgresql+psycopg2://")
    )

# Set the sync URL for alembic
sync_url = _make_sync_url(settings.database_url)
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_POSTGIS_SYSTEM_TABLES = {
    "spatial_ref_sys", "geometry_columns", "geography_columns",
    "raster_columns", "raster_overviews",
    "topology", "layer",
    "faces", "featnames", "edges", "addr", "addrfeat",
    "cousub", "county", "place", "state", "tract",
    "bg", "tabblock", "tabblock20", "zcta5",
    "zip_lookup", "zip_lookup_all", "zip_lookup_base",
    "zip_state", "zip_state_loc",
    "county_lookup", "countysub_lookup", "place_lookup", "state_lookup",
    "street_type_lookup", "secondary_unit_lookup", "direction_lookup",
    "geocode_settings", "geocode_settings_default",
    "loader_variables", "loader_platform", "loader_lookuptables",
    "pagc_gaz", "pagc_lex", "pagc_rules",
}


def include_object(obj, name, type_, reflected, compare_to):
    if type_ == "table":
        if name in _POSTGIS_SYSTEM_TABLES:
            return False
        schema = getattr(obj, "schema", None)
        if schema is not None and schema != "public":
            return False
    return True


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations using a synchronous psycopg2 connection."""
    from sqlalchemy import create_engine
    engine = create_engine(sync_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        do_run_migrations(connection)
    engine.dispose()


run_migrations_online()
