from __future__ import annotations
import re

INJECTION_PATTERNS = [
    re.compile(r"\bignore\s+(all\s+)?(previous|prior|above)\s+instructions?\b", re.I),
    re.compile(r"\bdisregard\s+(all\s+)?(previous|prior|above)\s+instructions?\b", re.I),
    re.compile(r"\breveal\s+(the\s+)?(system\s+prompt|hidden\s+instructions?|secrets?)\b", re.I),
    re.compile(r"\byou\s+are\s+now\s+(the\s+)?(system|admin|root|developer)\b", re.I),
]

def contains_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)

def sanitize_untrusted_text(text: str) -> str:
    # Keep document content as data, but make suspicious instruction-like phrases visible.
    for pattern in INJECTION_PATTERNS:
        text = pattern.sub("[SUSPICIOUS_INSTRUCTION_REMOVED]", text)
    return text

def normalize_role(role: str) -> str:
    allowed = {"admin", "staff", "user"}
    value = (role or "").strip().lower()
    if value not in allowed:
        raise ValueError(f"Unsupported role: {role}")
    return value
