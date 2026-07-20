from pydantic import BaseModel
from typing import Optional
import uuid


class ShelterResponse(BaseModel):
    name: str
    address: Optional[str] = None
    distance_km: float
    # Tri-state: True/False confirmed, None = unconfirmed (real data often blank).
    wheelchair_accessible: Optional[bool] = None
    ada_compliant: Optional[bool] = None
    generator_onsite: Optional[bool] = None
    asl_support: Optional[bool] = None
    pet_policy: str
    status: str
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    shelter_score: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    source: str
    phone: Optional[str] = None
    verified_by: Optional[uuid.UUID] = None


class ShelterUpdate(BaseModel):
    """Authority edit: any subset of these confirms/sets accessibility & status."""
    wheelchair_accessible: Optional[bool] = None
    ada_compliant: Optional[bool] = None
    generator_onsite: Optional[bool] = None
    asl_support: Optional[bool] = None
    pet_policy: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    status: Optional[str] = None
    phone: Optional[str] = None


class ShelterCreate(BaseModel):
    """Authority-seeded facility (school, church, etc.)."""
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    status: str = "open"
    wheelchair_accessible: Optional[bool] = None
    ada_compliant: Optional[bool] = None
    generator_onsite: Optional[bool] = None
    asl_support: Optional[bool] = None
    pet_policy: str = "unknown"
    phone: Optional[str] = None
