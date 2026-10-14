import re
from typing import Tuple, Optional

# Standard Educational Disclaimer attached to educational guidance
STANDARD_DISCLAIMER = (
    "Disclaimer: MediBot AI provides general educational health information only and does not provide "
    "a medical diagnosis, prognosis, or personalized treatment plan. Always consult a qualified physician or healthcare "
    "professional for medical advice. Never ignore, delay seeking, or discontinue prescribed medical care or medications "
    "based on information provided here."
)

# Emergency Warning Patterns (acute, life-threatening symptoms)
EMERGENCY_KEYWORDS = [
    r"\bchest\s+pain\b",
    r"\bcrushing\s+chest\b",
    r"\bpressure\s+in\s+chest\b",
    r"\bheart\s+attack\b",
    r"\bsevere\s+shortness\s+of\s+breath\b",
    r"\bcan\'?t\s+breathe\b",
    r"\bcannot\s+breathe\b",
    r"\bsuffocat(ing|ion)\b",
    r"\bthroat\s+closing\b",
    r"\banaphylax(is|ic)\b",
    r"\bface\s+droop(ing)?\b",
    r"\barm\s+weakness\b",
    r"\bspeech\s+slurred\b",
    r"\bslurred\s+speech\b",
    r"\bstroke\b",
    r"\bcough(ing)?\s+up\s+blood\b",
    r"\bvomit(ing)?\s+blood\b",
    r"\buncontrollable\s+bleeding\b",
    r"\bprofuse\s+bleeding\b",
    r"\bsuicid(e|al)\b",
    r"\bkill\s+myself\b",
    r"\bend\s+my\s+life\b",
    r"\bpoison(ing|ed)?\b",
    r"\boverdose\b",
    r"\bunconscious\b",
    r"\bunresponsive\b",
    r"\bseizure\b",
    r"\bsevere\s+head\s+injury\b"
]

EMERGENCY_REGEX = re.compile("|".join(EMERGENCY_KEYWORDS), re.IGNORECASE)

EMERGENCY_ADVISORY_MESSAGE = (
    "🚨 **EMERGENCY WARNING: IMMEDIATE MEDICAL ATTENTION REQUIRED**\n\n"
    "The symptoms or situation you mentioned may indicate an acute or life-threatening medical emergency. "
    "**Do not wait or rely on this chatbot.**\n\n"
    "- **Call your local emergency services immediately** (e.g., **911** in the US/Canada, **999** in the UK, **112** in Europe & India, or your local emergency number).\n"
    "- If you are alone, try to reach out to a nearby person or family member to assist you while waiting for emergency responders.\n"
    "- If you are experiencing suicidal thoughts or emotional crisis, please contact the Suicide & Crisis Lifeline by dialing or texting **988** (US/Canada) or call your local crisis line.\n\n"
    "*Do not attempt self-treatment or delay urgent medical care.*"
)


def check_emergency(user_text: str) -> Tuple[bool, Optional[str]]:
    """
    Scans the query for life-threatening or acute warning symptoms.
    Returns (is_emergency, emergency_response_message).
    """
    if not user_text or not isinstance(user_text, str):
        return False, None
    
    if EMERGENCY_REGEX.search(user_text):
        return True, EMERGENCY_ADVISORY_MESSAGE
    return False, None


def validate_chat_input(data: dict) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates the incoming chat payload.
    Returns (is_valid, cleaned_message, error_message).
    """
    if not isinstance(data, dict):
        return False, None, "Invalid request format. JSON object expected."
    
    message = data.get("message", "")
    if not isinstance(message, str):
        return False, None, "Message field must be a text string."
    
    cleaned_message = message.strip()
    if not cleaned_message:
        return False, None, "Message cannot be empty."
    
    if len(cleaned_message) > 2000:
        return False, None, "Message exceeds the maximum allowed length of 2000 characters."
    
    return True, cleaned_message, None
