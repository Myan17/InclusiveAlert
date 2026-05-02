"""initial_schema

Revision ID: ea53de92707b
Revises:
Create Date: 2026-05-02 12:49:03.569020

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ea53de92707b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Try to enable PostGIS — silently skip if not available
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        postgis_available = True
    except Exception:
        postgis_available = False

    op.create_table('audit_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('actor_id', sa.UUID(), nullable=True),
    sa.Column('action', sa.String(length=100), nullable=False),
    sa.Column('data_category', sa.String(length=50), nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('request_id', sa.String(length=100), nullable=True),
    sa.Column('emergency_context', sa.Boolean(), nullable=False),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('consent_policies',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('data_categories', sa.JSON(), nullable=False),
    sa.Column('release_conditions', sa.JSON(), nullable=False),
    sa.Column('allowed_recipients', sa.JSON(), nullable=False),
    sa.Column('expiry', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # hazard_events: use geometry column if PostGIS available, else skip geometry
    if postgis_available:
        import geoalchemy2
        op.create_table('hazard_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('hazard_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('certainty', sa.String(length=20), nullable=False),
        sa.Column('urgency', sa.String(length=20), nullable=False),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='MULTIPOLYGON', srid=4326, dimension=2, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
        sa.Column('area_description', sa.Text(), nullable=True),
        sa.Column('headline', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instruction', sa.Text(), nullable=True),
        sa.Column('effective_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_confidence', sa.Float(), nullable=False),
        sa.Column('raw_payload', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
        )
    else:
        op.create_table('hazard_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('hazard_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('certainty', sa.String(length=20), nullable=False),
        sa.Column('urgency', sa.String(length=20), nullable=False),
        sa.Column('area_description', sa.Text(), nullable=True),
        sa.Column('headline', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instruction', sa.Text(), nullable=True),
        sa.Column('effective_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_confidence', sa.Float(), nullable=False),
        sa.Column('raw_payload', sa.JSON(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
        )

    op.create_table('match_assignments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('hazard_event_id', sa.UUID(), nullable=False),
    sa.Column('primary_respondent_id', sa.UUID(), nullable=True),
    sa.Column('backup_respondent_id', sa.UUID(), nullable=True),
    sa.Column('score_breakdown', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('respondent_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('organization_id', sa.String(length=100), nullable=True),
    sa.Column('skills', sa.JSON(), nullable=False),
    sa.Column('languages', sa.JSON(), nullable=False),
    sa.Column('asl_level', sa.String(length=20), nullable=False),
    sa.Column('vehicle_type', sa.String(length=50), nullable=True),
    sa.Column('equipment', sa.JSON(), nullable=False),
    sa.Column('vetting_tier', sa.String(length=20), nullable=False),
    sa.Column('availability_status', sa.String(length=20), nullable=False),
    sa.Column('max_radius_km', sa.Float(), nullable=False),
    sa.Column('location_lat', sa.Float(), nullable=True),
    sa.Column('location_lon', sa.Float(), nullable=True),
    sa.Column('location_zip', sa.String(length=10), nullable=True),
    sa.Column('background_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )

    # shelters: use geometry if PostGIS available, else use lat/lon floats
    if postgis_available:
        import geoalchemy2
        op.create_table('shelters',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, dimension=2, spatial_index=False, from_text='ST_GeomFromEWKT', name='geometry', nullable=False), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_occupancy', sa.Integer(), nullable=True),
        sa.Column('wheelchair_accessible', sa.Boolean(), nullable=False),
        sa.Column('ada_compliant', sa.Boolean(), nullable=False),
        sa.Column('generator_onsite', sa.Boolean(), nullable=False),
        sa.Column('pet_policy', sa.String(length=20), nullable=False),
        sa.Column('population_types', sa.JSON(), nullable=False),
        sa.Column('asl_support', sa.Boolean(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_shelters_location', 'shelters', ['location'], unique=False, postgresql_using='gist')
    else:
        op.create_table('shelters',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('current_occupancy', sa.Integer(), nullable=True),
        sa.Column('wheelchair_accessible', sa.Boolean(), nullable=False),
        sa.Column('ada_compliant', sa.Boolean(), nullable=False),
        sa.Column('generator_onsite', sa.Boolean(), nullable=False),
        sa.Column('pet_policy', sa.String(length=20), nullable=False),
        sa.Column('population_types', sa.JSON(), nullable=False),
        sa.Column('asl_support', sa.Boolean(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )

    op.create_table('user_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('consent_policy_id', sa.UUID(), nullable=True),
    sa.Column('disability_needs', sa.JSON(), nullable=False),
    sa.Column('mobility_aids', sa.JSON(), nullable=False),
    sa.Column('communication_modes', sa.JSON(), nullable=False),
    sa.Column('medical_equipment', sa.JSON(), nullable=False),
    sa.Column('medication_dependency', sa.Boolean(), nullable=False),
    sa.Column('power_dependency', sa.Boolean(), nullable=False),
    sa.Column('service_animal', sa.Boolean(), nullable=False),
    sa.Column('caregiver_ids', sa.JSON(), nullable=False),
    sa.Column('preferred_language', sa.String(length=10), nullable=False),
    sa.Column('emergency_contacts', sa.JSON(), nullable=False),
    sa.Column('location_zip', sa.String(length=10), nullable=True),
    sa.Column('location_city', sa.String(length=100), nullable=True),
    sa.Column('location_state', sa.String(length=2), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )


def downgrade() -> None:
    op.drop_table('user_profiles')
    try:
        op.drop_index('idx_shelters_location', table_name='shelters', postgresql_using='gist')
    except Exception:
        pass
    op.drop_table('shelters')
    op.drop_table('respondent_profiles')
    op.drop_table('match_assignments')
    try:
        op.drop_index('idx_hazard_events_geometry', table_name='hazard_events', postgresql_using='gist')
    except Exception:
        pass
    op.drop_table('hazard_events')
    op.drop_table('consent_policies')
    op.drop_table('audit_events')
