# apps/api/app/services/matching_engine.py
"""
Matching engine: scores and ranks respondents for a given victim.

MatchScore formula (weights sum to 1.0):
    score = (
        0.25 * proximity_score       +  # inverse distance, same as shelter distance score
        0.25 * skill_fit_score       +  # how well respondent skills cover victim disability needs
        0.15 * availability_score    +  # availability_status on RespondentProfile
        0.15 * route_safety_score    +  # placeholder 0.5 (no live routing data)
        0.10 * trust_tier_score      +  # trust_tier 1-5 normalized to 0-1
        0.10 * communication_fit_score  # respondent communication_modes vs victim needs
    )
"""

from app.services.geofence import compute_distance_km

# Mapping from victim disability need → list of covering skills
SKILL_COVERAGE_MAP: dict[str, list[str]] = {
    "mobility_wheelchair": ["mobility_assistant", "first_aid"],
    "deaf": ["asl_interpreter", "sign_language"],
    "blind": ["guide_assistant", "first_aid"],
    "power_dependent": ["medical_technician", "first_aid"],
}


def _proximity_score(victim: dict, respondent: dict) -> float:
    """Closer respondent = higher score. 0 km → 1.0, 50 km → ~0.0."""
    r_lat = respondent.get("lat")
    r_lon = respondent.get("lon")
    if r_lat is None or r_lon is None:
        return 0.0
    v_lat = victim.get("lat")
    v_lon = victim.get("lon")
    if v_lat is None or v_lon is None:
        return 0.0
    distance_km = compute_distance_km(v_lat, v_lon, r_lat, r_lon)
    return max(0.0, 1.0 - (distance_km / 50.0))


def _skill_fit_score(victim: dict, respondent: dict) -> float:
    """Fraction of victim disability needs covered by at least one respondent skill."""
    needs: list[str] = victim.get("disability_needs") or []
    if not needs:
        return 1.0
    respondent_skills: set[str] = set(respondent.get("skills") or [])
    matched = 0
    for need in needs:
        covering_skills = SKILL_COVERAGE_MAP.get(need, [])
        if any(s in respondent_skills for s in covering_skills):
            matched += 1
    return matched / len(needs)


def _availability_score(respondent: dict) -> float:
    status = respondent.get("availability_status", "unavailable")
    mapping = {
        "available": 1.0,
        "on_break": 0.5,
        "unavailable": 0.0,
    }
    return mapping.get(status, 0.3)


def _route_safety_score() -> float:
    """Placeholder — no live routing data available."""
    return 0.5


def _trust_tier_score(respondent: dict) -> float:
    """Normalize trust_tier (1-5) to [0.0, 1.0]."""
    tier = respondent.get("trust_tier", 1)
    if tier is None:
        tier = 1
    tier = max(1, min(5, int(tier)))
    return (tier - 1) / 4.0


def _communication_fit_score(victim: dict, respondent: dict) -> float:
    """
    Check how well respondent's communication_modes match victim's communication needs.
    - "deaf" in needs → respondent needs "asl" or "text"
    - "blind" in needs → respondent needs "voice"
    Returns 1.0 if victim has no communication-related needs.
    """
    needs: list[str] = victim.get("disability_needs") or []
    comm_modes: set[str] = set(respondent.get("communication_modes") or [])

    communication_needs = []
    if "deaf" in needs:
        communication_needs.append("deaf")
    if "blind" in needs:
        communication_needs.append("blind")

    if not communication_needs:
        return 1.0

    matched = 0
    for need in communication_needs:
        if need == "deaf" and ("asl" in comm_modes or "text" in comm_modes):
            matched += 1
        elif need == "blind" and "voice" in comm_modes:
            matched += 1

    return matched / len(communication_needs)


def compute_match_score(victim: dict, respondent: dict) -> dict:
    """
    Compute the MatchScore for a single (victim, respondent) pair.

    Returns:
        {
            "respondent_id": str,
            "score": float,
            "breakdown": {
                "proximity": float,
                "skill_fit": float,
                "availability": float,
                "route_safety": float,
                "trust_tier": float,
                "communication_fit": float,
            }
        }
    """
    proximity = _proximity_score(victim, respondent)
    skill_fit = _skill_fit_score(victim, respondent)
    availability = _availability_score(respondent)
    route_safety = _route_safety_score()
    trust_tier = _trust_tier_score(respondent)
    communication_fit = _communication_fit_score(victim, respondent)

    score = (
        0.25 * proximity +
        0.25 * skill_fit +
        0.15 * availability +
        0.15 * route_safety +
        0.10 * trust_tier +
        0.10 * communication_fit
    )
    score = round(min(1.0, max(0.0, score)), 4)

    return {
        "respondent_id": str(respondent.get("respondent_id", "")),
        "score": score,
        "breakdown": {
            "proximity": round(proximity, 4),
            "skill_fit": round(skill_fit, 4),
            "availability": round(availability, 4),
            "route_safety": round(route_safety, 4),
            "trust_tier": round(trust_tier, 4),
            "communication_fit": round(communication_fit, 4),
        },
    }


def rank_respondents(victim: dict, respondents: list[dict]) -> list[dict]:
    """
    Score all respondents for a victim and return them sorted by score descending.

    Each item is the dict from compute_match_score.
    """
    scored = [compute_match_score(victim, r) for r in respondents]
    return sorted(scored, key=lambda x: x["score"], reverse=True)
