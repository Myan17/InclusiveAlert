# apps/api/app/schemas/match_assignment.py
from pydantic import BaseModel


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
