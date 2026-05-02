# apps/api/app/schemas/respondent_profile.py
import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class RespondentProfileCreate(BaseModel):
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["en"])
    asl_level: str = "none"
    vehicle_type: Optional[str] = None
    equipment: list[str] = Field(default_factory=list)
    vetting_tier: str = "neighbor"
    availability_status: str = "unavailable"
    max_radius_km: float = 10.0
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_zip: Optional[str] = None
    organization_id: Optional[str] = None
    background_verified: bool = False


class RespondentProfileResponse(RespondentProfileCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
