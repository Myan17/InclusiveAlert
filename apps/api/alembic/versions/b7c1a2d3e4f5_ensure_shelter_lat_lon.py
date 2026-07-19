"""ensure shelters.lat/lon exist (model always maps them; PostGIS branch omitted them)

The Shelter model unconditionally maps `lat`/`lon`, but the initial migration's
PostGIS branch created only the `location` geometry column. On a PostGIS
deployment that mismatch makes every `select(Shelter)` reference nonexistent
columns and fail. This migration adds the columns if missing and backfills them
from `location`, so the ORM entity matches the table on all deployments.

Revision ID: b7c1a2d3e4f5
Revises: fa4369716818
Create Date: 2026-07-18
"""
from typing import Union
import sqlalchemy as sa
from alembic import op

revision: str = "b7c1a2d3e4f5"
down_revision: Union[str, None] = "fa4369716818"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("shelters")}

    if "lat" not in cols:
        op.add_column("shelters", sa.Column("lat", sa.Float(), nullable=True))
    if "lon" not in cols:
        op.add_column("shelters", sa.Column("lon", sa.Float(), nullable=True))

    # Backfill from the PostGIS geometry when present, so the non-PostGIS
    # read path also has coordinates.
    if "location" in cols:
        op.execute(
            "UPDATE shelters SET lat = ST_Y(location), lon = ST_X(location) "
            "WHERE lat IS NULL OR lon IS NULL"
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("shelters")}
    if "lon" in cols:
        op.drop_column("shelters", "lon")
    if "lat" in cols:
        op.drop_column("shelters", "lat")
