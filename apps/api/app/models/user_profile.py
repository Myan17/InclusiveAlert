# apps/api/app/models/user_profile.py
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ConsentPolicy(Base):
    __tablename__ = "consent_policies"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    data_categories: Mapped[list] = mapped_column(JSON, default=list)
    release_conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    allowed_recipients: Mapped[list] = mapped_column(JSON, default=list)
    expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="victim")
    consent_policy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    disability_needs: Mapped[list] = mapped_column(JSON, default=list)
    mobility_aids: Mapped[list] = mapped_column(JSON, default=list)
    communication_modes: Mapped[list] = mapped_column(JSON, default=list)
    medical_equipment: Mapped[list] = mapped_column(JSON, default=list)
    medication_dependency: Mapped[bool] = mapped_column(Boolean, default=False)
    power_dependency: Mapped[bool] = mapped_column(Boolean, default=False)
    service_animal: Mapped[bool] = mapped_column(Boolean, default=False)
    caregiver_ids: Mapped[list] = mapped_column(JSON, default=list)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en")
    emergency_contacts: Mapped[list] = mapped_column(JSON, default=list)
    location_zip: Mapped[str | None] = mapped_column(String(10), nullable=True)
    location_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
