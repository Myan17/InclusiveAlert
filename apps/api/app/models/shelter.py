# apps/api/app/models/shelter.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Float, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

# Try to import PostGIS — gracefully degrade if not available
try:
    from geoalchemy2 import Geometry
    _POSTGIS = True
except ImportError:
    _POSTGIS = False


class Shelter(Base):
    __tablename__ = "shelters"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PostGIS geometry column — only used when PostGIS is available
    if _POSTGIS:
        location: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=True)
    
    # Plain lat/lon fallback — always present
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="open")
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_occupancy: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Accessibility attributes are TRI-STATE: True/False = confirmed,
    # None = unconfirmed (real feeds usually leave these blank). Never guess.
    wheelchair_accessible: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ada_compliant: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    generator_onsite: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    asl_support: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    pet_policy: Mapped[str] = mapped_column(String(20), default="unknown")
    population_types: Mapped[list] = mapped_column(JSON, default=list)

    # Provenance: where the row came from and who confirmed the accessibility.
    source: Mapped[str] = mapped_column(String(50), default="fema_nss")
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
