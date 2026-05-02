# apps/api/app/models/respondent_profile.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class RespondentProfile(Base):
    __tablename__ = "respondent_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    organization_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    asl_level: Mapped[str] = mapped_column(String(20), default="none")
    vehicle_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    equipment: Mapped[list] = mapped_column(JSON, default=list)
    vetting_tier: Mapped[str] = mapped_column(String(20), default="neighbor")
    availability_status: Mapped[str] = mapped_column(String(20), default="unavailable", index=True)
    max_radius_km: Mapped[float] = mapped_column(Float, default=10.0)
    location_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)
    background_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
