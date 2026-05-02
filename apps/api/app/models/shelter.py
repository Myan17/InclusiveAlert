# apps/api/app/models/shelter.py
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Float, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.database import Base


class Shelter(Base):
    __tablename__ = "shelters"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open")
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_occupancy: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wheelchair_accessible: Mapped[bool] = mapped_column(Boolean, default=False)
    ada_compliant: Mapped[bool] = mapped_column(Boolean, default=False)
    generator_onsite: Mapped[bool] = mapped_column(Boolean, default=False)
    pet_policy: Mapped[str] = mapped_column(String(20), default="no_pets")
    population_types: Mapped[list] = mapped_column(JSON, default=list)
    asl_support: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(50), default="fema_nss")
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
