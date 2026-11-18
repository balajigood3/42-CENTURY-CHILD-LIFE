"""Small transparent checks for low-resource language outputs."""
import re

def script_match_ratio(text: str, expected_script: str) -> float:
    if not text.strip():
        return 0.0
    from .language import RANGES
    script_range = next(((a, b) for name, a, b in RANGES if name == expected_script), None)
    if script_range is None:
        return 0.0
    start, end = script_range
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(start <= ord(c) <= end for c in letters) / len(letters)

def basic_output_checks(text: str) -> dict:
    return {
        "non_empty": bool(text.strip()),
        "word_count": len(re.findall(r"\S+", text)),
        "contains_replacement_character": "\ufffd" in text,
        "has_control_characters": any(ord(c) < 32 and c not in "\\n\\t\\r" for c in text),
    }
