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
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Tables that belong to PostGIS / Tiger geocoder extensions — never manage these.
_POSTGIS_SYSTEM_TABLES = {
    "spatial_ref_sys", "geometry_columns", "geography_columns",
    "raster_columns", "raster_overviews",
    # topology extension
    "topology", "layer",
    # tiger geocoder
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
    """Exclude PostGIS/Tiger system tables and non-public schemas from migrations."""
    if type_ == "table":
        if name in _POSTGIS_SYSTEM_TABLES:
            return False
        # Only manage tables in the public schema
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


async def run_async_migrations():
    engine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


run_migrations_online()
