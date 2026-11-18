from config import MAX_INPUT_CHARS
from core.llm import ask_json
from core.prompts import ANALYSIS_PROMPT

ALLOWED_LEVELS = {"LOW", "MEDIUM", "HIGH", "INSUFFICIENT_INFORMATION"}

def _string_list(value):
    if not isinstance(value, list):
        return []
    return [str(x) for x in value if str(x).strip()]

def analyze_uncertainty(question, context=""):
    question, context = question.strip(), context.strip()
    if not question:
        raise ValueError("கேள்வி காலியாக இருக்கக்கூடாது.")
    if len(question) > MAX_INPUT_CHARS or len(context) > MAX_INPUT_CHARS:
        raise ValueError(f"Input {MAX_INPUT_CHARS} characters-க்குள் இருக்க வேண்டும்.")
    raw = ask_json(ANALYSIS_PROMPT.format(
        question=question, context=context or "[கூடுதல் context வழங்கப்படவில்லை]"
    ))
    level = str(raw.get("uncertainty_level", "INSUFFICIENT_INFORMATION")).upper()
    if level not in ALLOWED_LEVELS:
        level = "INSUFFICIENT_INFORMATION"
    answer = str(raw.get("answer", "")).strip()
    if not answer:
        answer = "கிடைத்த தகவல்களின் அடிப்படையில் நம்பகமான பதிலை உருவாக்க முடியவில்லை."
        level = "INSUFFICIENT_INFORMATION"
    return {
        "answer": answer,
        "uncertainty_level": level,
        "uncertainty_reasons": _string_list(raw.get("uncertainty_reasons")),
        "assumptions": _string_list(raw.get("assumptions")),
        "missing_information": _string_list(raw.get("missing_information")),
        "confidence_explanation": str(raw.get("confidence_explanation", "")).strip()
            or "Confidence-ஐ நம்பகமாக அளவிட போதுமான தகவல் இல்லை."
    }
