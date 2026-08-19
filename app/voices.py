"""Allowlisted Kokoro voices. Unknown names are rejected at the API boundary."""

DEFAULT_VOICE = "am_michael"

VOICES: dict[str, str] = {
    "am_michael": "American male, confident, firm but gentle",
    "am_adam": "American male, warm, smooth",
    "am_liam": "American male, friendly, grounded",
    "am_eric": "American male, steady, calm",
    "am_james": "American male, confident, refined",
    "am_william": "American male, classic, authoritative",
    "am_caleb": "American male, youthful, earnest",
    "am_david": "American male, strong, measured",
    "am_ethan": "American male, warm, engaging",
    "bm_daniel": "British male, light, refined",
    "bm_george": "British male, classic BBC",
    "bm_lewis": "British male, youthful",
    "bm_oliver": "British male, bright, modern",
    "af_heart": "American female, warm, versatile",
    "af_nova": "American female, smooth, melodic",
    "af_sarah": "American female, soft, natural",
    "af_bella": "American female, warm, gentle",
    "bf_emma": "British female, clear, warm",
    "bf_isabella": "British female, elegant, refined",
}

SAMPLE_RATE = 24000
MAX_TEXT_CHARS = 8000


def known_voice(name: str) -> bool:
    return name in VOICES
