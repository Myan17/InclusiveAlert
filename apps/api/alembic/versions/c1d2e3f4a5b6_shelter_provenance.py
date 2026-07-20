"""shelter provenance + nullable accessibility (tri-state)

Accessibility attributes become nullable (NULL = unconfirmed) and provenance
columns are added so real-feed data and authority confirmations are distinct.

Revision ID: c1d2e3f4a5b6
Revises: b7c1a2d3e4f5
Create Date: 2026-07-20
"""
from typing import Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "b7c1a2d3e4f5"
branch_labels = None
depends_on = None

_ACCESS_COLS = ["wheelchair_accessible", "ada_compliant", "generator_onsite", "asl_support"]


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("shelters")}

    for col in _ACCESS_COLS:
        if col in cols:
            op.alter_column("shelters", col, existing_type=sa.Boolean(), nullable=True)

    if "phone" not in cols:
        op.add_column("shelters", sa.Column("phone", sa.String(length=50), nullable=True))
    if "verified_by" not in cols:
        op.add_column("shelters", sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True))
    if "last_synced_at" not in cols:
        op.add_column("shelters", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("shelters")}
    for col in ("last_synced_at", "verified_by", "phone"):
        if col in cols:
            op.drop_column("shelters", col)
    # Backfill NULLs before restoring NOT NULL, so downgrade can't fail.
    for col in _ACCESS_COLS:
        if col in cols:
            op.execute(f"UPDATE shelters SET {col} = false WHERE {col} IS NULL")
            op.alter_column("shelters", col, existing_type=sa.Boolean(), nullable=False)
