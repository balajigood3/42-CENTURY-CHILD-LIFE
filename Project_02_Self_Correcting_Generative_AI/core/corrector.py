from core.generator import generate
from prompts.templates import CORRECTION_PROMPT

def correct_answer(question: str, answer: str, evaluation: dict, context: str = "") -> str:
    prompt = CORRECTION_PROMPT.format(
        question=question,
        answer=answer,
        evaluation=evaluation.get("details", ""),
        context=context or "[ஆதார Context வழங்கப்படவில்லை]"
    )
    return generate(prompt)
