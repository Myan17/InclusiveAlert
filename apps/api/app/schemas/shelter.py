from pydantic import BaseModel
from typing import Optional

class ShelterResponse(BaseModel):
    name: str
    address: Optional[str] = None
    distance_km: float
    wheelchair_accessible: bool
    ada_compliant: bool
    generator_onsite: bool
    pet_policy: str
    status: str
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    shelter_score: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    source: str
