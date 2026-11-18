"""Tamil-English code-mixed text normalization and lightweight language cues."""
from __future__ import annotations
import re

TAMIL_RANGE = re.compile(r"[\u0B80-\u0BFF]")
LATIN_RANGE = re.compile(r"[A-Za-z]")

PHRASE_MAP = {
    "ai na enna": "AI என்றால் என்ன",
    "rag na enna": "RAG என்றால் என்ன",
    "machine learning na enna": "Machine Learning என்றால் என்ன",
    "epdi work aagum": "எப்படி செயல்படும்",
    "meaning sollu": "அர்த்தம் சொல்லுங்கள்",
    "explain pannunga": "விளக்குங்கள்",
    "simple ah sollu": "எளிமையாகச் சொல்லுங்கள்",
    "example kudu": "உதாரணம் கொடுங்கள்",
    "thanks": "நன்றி",
    "vanakkam": "வணக்கம்",
}

def detect_script_mix(text: str) -> dict:
    tamil_count = len(TAMIL_RANGE.findall(text))
    latin_count = len(LATIN_RANGE.findall(text))
    if tamil_count and latin_count:
        label = "tamil_english_mixed"
    elif tamil_count:
        label = "tamil"
    elif latin_count:
        label = "english_or_transliterated"
    else:
        label = "other_or_empty"
    return {"label": label, "tamil_characters": tamil_count, "latin_characters": latin_count}

def normalize_code_mixed(text: str) -> str:
    """Normalize common romanized Tamil phrases; preserve unknown text."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    # Longest keys first to avoid partial phrase substitutions.
    for source, target in sorted(PHRASE_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = re.sub(r"(?<!\w)" + re.escape(source) + r"(?!\w)", target, normalized)
    return re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), normalized)

def extract_terms(text: str) -> list[str]:
    """Extract simple Latin/Tamil tokens; this is not morphological analysis."""
    return re.findall(r"[A-Za-z0-9_+#.-]+|[\u0B80-\u0BFF]+", text)
