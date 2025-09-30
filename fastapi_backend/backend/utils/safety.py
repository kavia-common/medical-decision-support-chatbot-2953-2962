from utils.config import get_settings

# PUBLIC_INTERFACE
def add_disclaimers(payload: dict) -> dict:
    """Attach medical disclaimers and safety warnings to a response payload."""
    settings = get_settings()
    payload["disclaimer"] = settings.MEDICAL_DISCLAIMER
    payload["safety_warnings"] = settings.SAFETY_WARNINGS
    return payload
