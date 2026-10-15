import re
from typing import Tuple, Optional

# Standard Educational Disclaimer attached to educational guidance
STANDARD_DISCLAIMER = (
    "Disclaimer: MediBot AI provides general educational health information only and does not provide "
    "a medical diagnosis, prognosis, or personalized treatment plan. Always consult a qualified physician or healthcare "
    "professional for medical advice. Never ignore, delay seeking, or discontinue prescribed medical care or medications "
    "based on information provided here."
)

# 1. Left Extremity (Arm / Hand) + Cardiac Accompanying Symptoms
LEFT_EXTREMITY_PATTERN = re.compile(
    r"\b(left\s+(arm|hand|wrist|shoulder|elbow)|radiat(ing|ed|es|ion)\s+(to|down|into)\s+(the\s+)?(left\s+)?(arm|hand))\b",
    re.IGNORECASE
)

CARDIAC_ACCOMPANYING_PATTERNS = [
    r"\bchest\b",
    r"\bpressure\b",
    r"\btightness\b",
    r"\bheaviness\b",
    r"\bsqueezing\b",
    r"\bshortness\s+of\s+breath\b",
    r"\b(can\'?t|cannot|trouble|difficult(y)?)\s+breath(e|ing)\b",
    r"\bbreathless\b",
    r"\bsweat(ing|y)?\b",
    r"\bcold\s+sweat\b",
    r"\bdiaphor(esis|etic)\b",
    r"\bnausea\b",
    r"\bnauseous\b",
    r"\bvomit(ing)?\b",
    r"\bfaint(ing|ness)?\b",
    r"\bdizz(y|iness)\b",
    r"\blightheaded(ness)?\b",
    r"\bheart\s+attack\b",
    r"\bangina\b",
    r"\bpalpitat(ion|ions)\b",
    r"\bracing\s+heart\b",
    r"\bsudden(\s+severe)?\b",
    r"\bsevere\b"
]
CARDIAC_ACCOMPANYING_REGEX = re.compile("|".join(CARDIAC_ACCOMPANYING_PATTERNS), re.IGNORECASE)

CARDIAC_EMERGENCY_ADVISORY = (
    "🚨 **EMERGENCY WARNING: POTENTIAL CARDIAC EVENT / IMMEDIATE MEDICAL ATTENTION REQUIRED**\n\n"
    "You have reported symptoms involving left arm or left hand discomfort accompanied by warning signs "
    "(such as chest pain or pressure, shortness of breath, cold sweating, nausea, faintness, or sudden symptoms). "
    "These warning signs may indicate an acute coronary event or **heart attack**.\n\n"
    "**Important:** Mild or slight pain does **not** rule out a life-threatening cardiac emergency.\n\n"
    "**ACTIONS TO TAKE IMMEDIATELY:**\n"
    "- **Call local emergency services immediately:** Dial **112** in India and Europe, **911** in the US/Canada, or **999** in the UK.\n"
    "- **Cease physical exertion** and sit down in a safe, resting position.\n"
    "- **Do not wait or delay emergency advice** to ask further questions or search the knowledge base.\n"
    "- If someone is nearby, notify them immediately so they can assist you while emergency responders arrive.\n\n"
    "*This triage alert is a conservative safety warning and is not a definitive medical diagnosis.*"
)

# 2. Stroke Emergency Patterns (FAST criteria)
STROKE_PATTERNS = [
    r"\bstroke\b",
    r"\btransient\s+ischemic\b",
    r"\btia\b",
    r"\bface\s+droop(ing)?\b",
    r"\bfacial\s+droop(ing)?\b",
    r"\b(slurred\s+speech|speech\s+slurred)\b",
    r"\b(trouble|difficulty|unable\s+to|can\'?t)\s+speak(ing)?\b",
    r"\b(loss\s+of\s+speech|garbled\s+speech)\b",
    r"\barm\s+weakness\b",
    r"\bweakness\s+(in|of)\s+(one|my|the)\s+arm\b",
    r"\b(sudden\s+weakness|sudden\s+numbness)\b",
    r"\bone-?sided\s+(weakness|numbness|paralysis)\b",
    r"\bnumbness\s+(in|of|on)\s+(one\s+side|half)\s+(of\s+)?(face|body|arm)\b"
]
STROKE_REGEX = re.compile("|".join(STROKE_PATTERNS), re.IGNORECASE)

STROKE_EMERGENCY_ADVISORY = (
    "🚨 **EMERGENCY WARNING: URGENT STROKE WARNING SIGNS DETECTED**\n\n"
    "The symptoms you described (sudden weakness, numbness, facial drooping, or speech difficulty) are critical warning signs of a **stroke**.\n\n"
    "**REMEMBER F.A.S.T.:**\n"
    "- **F (Face):** Is one side of the face drooping or numb?\n"
    "- **A (Arms):** Is one arm weak or numb, or drifting downward when raised?\n"
    "- **S (Speech):** Is speech slurred, strange, or difficult to produce?\n"
    "- **T (Time):** **Time is critical.** Rapid medical intervention preserves brain tissue.\n\n"
    "**ACTIONS TO TAKE IMMEDIATELY:**\n"
    "- **Call local emergency services immediately:** Dial **112** in India & Europe, **911** in the US/Canada, or **999** in the UK.\n"
    "- Note the exact time symptoms started.\n"
    "- **Do not wait or delay.** Do not attempt to sleep it off.\n\n"
    "*This triage alert is a conservative safety warning and is not a definitive medical diagnosis.*"
)

# 3. Acute General Medical Emergencies
GENERAL_EMERGENCY_PATTERNS = [
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
    r"\bcough(ing)?\s+up\s+blood\b",
    r"\bvomit(ing)?\s+blood\b",
    r"\buncontrollable\s+bleeding\b",
    r"\bprofuse\s+bleeding\b",
    r"\bhemorrhag(e|ing)\b",
    r"\bsuicid(e|al)\b",
    r"\bkill\s+myself\b",
    r"\bend\s+my\s+life\b",
    r"\bpoison(ing|ed)?\b",
    r"\boverdose\b",
    r"\bunconscious\b",
    r"\bunresponsive\b",
    r"\bseizure\b",
    r"\bconvuls(ing|ion)\b",
    r"\bsevere\s+head\s+injury\b",
    r"\bthunderclap\s+headache\b"
]
GENERAL_EMERGENCY_REGEX = re.compile("|".join(GENERAL_EMERGENCY_PATTERNS), re.IGNORECASE)

GENERAL_EMERGENCY_ADVISORY = (
    "🚨 **EMERGENCY WARNING: IMMEDIATE MEDICAL ATTENTION REQUIRED**\n\n"
    "The symptoms or situation you mentioned may indicate an acute or life-threatening medical emergency. "
    "**Do not wait or rely on this chatbot.**\n\n"
    "- **Call your local emergency services immediately:** Dial **112** in India & Europe, **911** in the US/Canada, **999** in the UK, or your local emergency number.\n"
    "- If you are alone, try to reach out to a nearby person or family member to assist you while waiting for emergency responders.\n"
    "- If you are experiencing suicidal thoughts or emotional crisis, please contact the Suicide & Crisis Lifeline by dialing or texting **988** (US/Canada), **112** / **9152987821** (India), or your local crisis line.\n\n"
    "*Do not attempt self-treatment or delay urgent medical care. This safety triage advisory is not a medical diagnosis.*"
)


def check_emergency(user_text: str) -> Tuple[bool, Optional[str]]:
    """
    Scans the query for life-threatening or acute warning symptoms prior to RAG retrieval.
    Triage order:
    1. Stroke warning signs (sudden weakness/numbness, facial drooping, speech difficulty).
    2. Left arm or left hand discomfort combined with cardiac warning signs (chest pressure, shortness of breath, nausea, sweating, faintness, sudden onset).
       Note: Mild pain does not rule out emergency.
    3. Acute general medical emergencies (severe chest pain, respiratory arrest, anaphylaxis, severe bleeding, overdose, unconsciousness).
    
    Returns:
        (is_emergency: bool, emergency_response_message: Optional[str])
    """
    if not user_text or not isinstance(user_text, str):
        return False, None

    text_lower = user_text.lower().strip()

    # 1. Stroke check
    if STROKE_REGEX.search(text_lower):
        return True, STROKE_EMERGENCY_ADVISORY

    # 2. Left arm / left hand + cardiac warning signs
    if LEFT_EXTREMITY_PATTERN.search(text_lower):
        if CARDIAC_ACCOMPANYING_REGEX.search(text_lower):
            return True, CARDIAC_EMERGENCY_ADVISORY

    # 3. Acute general emergencies
    if GENERAL_EMERGENCY_REGEX.search(text_lower):
        return True, GENERAL_EMERGENCY_ADVISORY

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
