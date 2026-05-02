# apps/api/app/services/personalized_alert.py
"""
Personalized, disability-aware emergency alert generation.

No external dependencies — pure computation over dicts.
"""


def _map_urgency(urgency_level: str | None) -> str:
    if urgency_level == "Immediate":
        return "immediate"
    if urgency_level == "Expected":
        return "watch"
    return "advisory"


def _build_channels(disability_needs: list[str]) -> list[str]:
    channels: list[str] = ["push_notification"]

    if not disability_needs:
        channels.append("sms")
        channels.append("voice_call")
        return channels

    if "deaf" in disability_needs:
        channels.append("sms")
        channels.append("visual_alert")
        # voice_call intentionally excluded for deaf users

    if "blind" in disability_needs:
        channels.append("voice_call")
        # visual_alert not added here unless already present

    if "mobility_wheelchair" in disability_needs and "sms" not in channels:
        channels.append("sms")

    if "power_dependent" in disability_needs and "sms" not in channels:
        channels.append("sms")

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for ch in channels:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return result


def _build_instructions(event_type: str, disability_needs: list[str], service_animal: bool) -> list[str]:
    instructions: list[str] = []

    if "Tornado" in event_type:
        instructions.append("Seek shelter immediately in an interior room on the lowest floor.")
    elif "Flood" in event_type or "Hurricane" in event_type:
        instructions.append("Move to higher ground immediately. Do not walk through moving water.")
    elif "Earthquake" in event_type:
        instructions.append("Drop, Cover, and Hold On. Stay away from windows.")
    elif "Fire" in event_type:
        instructions.append("Evacuate immediately. Follow posted evacuation routes.")
    else:
        instructions.append("Follow instructions from local emergency management.")

    if "mobility_wheelchair" in disability_needs:
        instructions.append("Request accessible transportation assistance by calling 211.")
        instructions.append("Identify your nearest accessible shelter before evacuating.")

    if "deaf" in disability_needs:
        instructions.append("Monitor visual alerts and text-based emergency notifications.")
        instructions.append("Alert nearby people to your location using visual signals.")

    if "blind" in disability_needs:
        instructions.append("Contact a trusted person or neighbor for navigation assistance.")
        instructions.append("Keep your phone available for voice-based emergency updates.")

    if "power_dependent" in disability_needs:
        instructions.append("Notify your power company immediately — you are on the medical baseline list.")
        instructions.append("Have backup power for medical equipment; activate now if power may be disrupted.")

    if service_animal:
        instructions.append("Bring your service animal's emergency kit (food, water, documentation).")

    return instructions


def generate_alert_message(user_profile: dict, hazard: dict) -> dict:
    """
    Generate a personalized emergency alert for a user given a hazard event.

    Returns a dict with subject, body, channels, instructions, and urgency.
    """
    disability_needs: list[str] = user_profile.get("disability_needs") or []
    service_animal: bool = bool(user_profile.get("service_animal", False))

    event_type: str = hazard.get("event_type", "Emergency Alert")
    area_description: str | None = hazard.get("area_description")
    description: str | None = hazard.get("description")
    urgency_level: str | None = hazard.get("urgency_level")

    subject = f"{event_type} — Emergency Alert"
    base_body = f"A {event_type} has been issued for {area_description or 'your area'}."
    body = f"{base_body} {description}".strip() if description else base_body
    channels = _build_channels(disability_needs)
    instructions = _build_instructions(event_type, disability_needs, service_animal)
    urgency = _map_urgency(urgency_level)

    return {
        "subject": subject,
        "body": body,
        "channels": channels,
        "instructions": instructions,
        "urgency": urgency,
    }


def should_notify(user_profile: dict, hazard: dict) -> bool:
    """
    Determine whether a user should be notified given a hazard event.

    Power-dependent users are notified regardless of severity.
    """
    disability_needs: list[str] = user_profile.get("disability_needs") or []
    severity: str | None = hazard.get("severity")

    if "power_dependent" in disability_needs:
        return True

    if severity in ("Extreme", "Severe", "Moderate"):
        return True

    if severity in ("Minor", "Unknown") or severity is None:
        return False

    return True  # unknown severity string — default to notifying
