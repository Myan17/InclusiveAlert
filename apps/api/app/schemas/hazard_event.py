# apps/api/app/schemas/hazard_event.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class HazardEventResponse(BaseModel):
    id: uuid.UUID
    external_id: str
    source: str
    hazard_type: str
    severity: str
    certainty: str
    urgency: str
    headline: Optional[str]
    description: Optional[str]
    instruction: Optional[str]
    area_description: Optional[str]
    effective_at: datetime
    expires_at: Optional[datetime]
    source_confidence: float
    is_active: bool

    model_config = {"from_attributes": True}
