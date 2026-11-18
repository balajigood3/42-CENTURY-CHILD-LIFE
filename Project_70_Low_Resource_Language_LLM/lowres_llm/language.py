"""Language metadata and lightweight Unicode script identification."""
LANGUAGES = {
    "Tamil": {"code": "ta", "script": "Tamil"},
    "Hindi": {"code": "hi", "script": "Devanagari"},
    "Telugu": {"code": "te", "script": "Telugu"},
    "Kannada": {"code": "kn", "script": "Kannada"},
    "Malayalam": {"code": "ml", "script": "Malayalam"},
    "Bengali": {"code": "bn", "script": "Bengali"},
    "Marathi": {"code": "mr", "script": "Devanagari"},
    "Gujarati": {"code": "gu", "script": "Gujarati"},
    "Punjabi": {"code": "pa", "script": "Gurmukhi"},
    "Odia": {"code": "or", "script": "Odia"},
    "English": {"code": "en", "script": "Latin"},
}
RANGES = [
    ("Tamil", 0x0B80, 0x0BFF),
    ("Devanagari", 0x0900, 0x097F),
    ("Telugu", 0x0C00, 0x0C7F),
    ("Kannada", 0x0C80, 0x0CFF),
    ("Malayalam", 0x0D00, 0x0D7F),
    ("Bengali", 0x0980, 0x09FF),
    ("Gujarati", 0x0A80, 0x0AFF),
    ("Gurmukhi", 0x0A00, 0x0A7F),
    ("Odia", 0x0B00, 0x0B7F),
    ("Latin", 0x0041, 0x007A),
]

def detect_script(text: str) -> str:
    counts = {}
    for char in text:
        codepoint = ord(char)
        for name, start, end in RANGES:
            if start <= codepoint <= end:
                counts[name] = counts.get(name, 0) + 1
                break
    return max(counts, key=counts.get) if counts else "Unknown"

def language_names():
    return list(LANGUAGES.keys())
