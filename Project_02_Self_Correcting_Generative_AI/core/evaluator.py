import re
from config import PASS_SCORE
from core.generator import generate
from prompts.templates import EVALUATION_PROMPT

def evaluate(question: str, answer: str, context: str = "") -> dict:
    prompt = EVALUATION_PROMPT.format(
        question=question,
        answer=answer,
        context=context or "[ஆதார Context வழங்கப்படவில்லை]"
    )
    details = generate(prompt)
    score_match = re.search(r"(?im)^SCORE:\s*(\d{1,3})\s*$", details)
    status_match = re.search(r"(?im)^STATUS:\s*(PASS|FAIL)\s*$", details)
    if not score_match or not status_match:
        return {"score": 0, "status": "FAIL", "details": details,
                "parse_error": "Evaluator எதிர்பார்த்த வடிவில் பதிலளிக்கவில்லை."}
    score = min(100, int(score_match.group(1)))
    # PASS requires both model's PASS and configured minimum score.
    status = "PASS" if status_match.group(1).upper() == "PASS" and score >= PASS_SCORE else "FAIL"
    return {"score": score, "status": status, "details": details}
