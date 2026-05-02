# apps/api/app/schemas/user_profile.py
import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional


class VictimProfileUpdate(BaseModel):
    disability_needs: list[str] = []
    mobility_aids: list[str] = []
    communication_modes: list[str] = []
    medical_equipment: list[str] = []
    medication_dependency: bool = False
    power_dependency: bool = False
    service_animal: bool = False
    caregiver_ids: list[str] = []
    preferred_language: str = "en"
    emergency_contacts: list[dict] = []
    location_zip: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None


class VictimProfileResponse(VictimProfileUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
