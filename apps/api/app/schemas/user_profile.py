# apps/api/app/schemas/user_profile.py
import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class VictimProfileUpdate(BaseModel):
    disability_needs: list[str] = Field(default_factory=list)
    mobility_aids: list[str] = Field(default_factory=list)
    communication_modes: list[str] = Field(default_factory=list)
    medical_equipment: list[str] = Field(default_factory=list)
    medication_dependency: bool = False
    power_dependency: bool = False
    service_animal: bool = False
    caregiver_ids: list[str] = Field(default_factory=list)
    preferred_language: str = "en"
    emergency_contacts: list[dict] = Field(default_factory=list)
    location_zip: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None


class VictimProfileResponse(VictimProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
