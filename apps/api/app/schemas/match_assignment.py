# apps/api/app/schemas/match_assignment.py
from pydantic import BaseModel
from typing import Optional


class MatchBreakdown(BaseModel):
    proximity: float
    skill_fit: float
    availability: float
    route_safety: float
    trust_tier: float
    communication_fit: float


class MatchResult(BaseModel):
    respondent_id: str
    score: float
    breakdown: MatchBreakdown


class MatchAssignmentResponse(BaseModel):
    results: list[MatchResult]
    total: int


# ── Victim summary for respondent view ───────────────────────────────────────

class VictimSummary(BaseModel):
    user_id: str
    email: str
    disability_needs: list[str]
    communication_modes: list[str]
    service_animal: bool
    power_dependency: bool
    location_zip: Optional[str]
    location_city: Optional[str]
    location_state: Optional[str]
    urgency_score: float   # 0–1 based on active alerts + needs severity


class VictimListResponse(BaseModel):
    victims: list[VictimSummary]
    total: int
