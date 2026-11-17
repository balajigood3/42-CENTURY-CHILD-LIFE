from config import MAX_RETRIES
from core.generator import generate
from core.evaluator import evaluate
from core.corrector import correct_answer
from prompts.templates import GENERATION_PROMPT

def run_pipeline(question: str, context: str = "") -> dict:
    prompt = GENERATION_PROMPT.format(
        question=question,
        context=context or "[ஆதார Context வழங்கப்படவில்லை]"
    )
    initial_answer = generate(prompt)
    current_answer = initial_answer
    history = []
    evaluation = evaluate(question, current_answer, context)
    history.append({"iteration": 0, "answer": current_answer,
                    "score": evaluation["score"], "status": evaluation["status"]})

    for attempt in range(MAX_RETRIES):
        if evaluation["status"] == "PASS":
            break
        revised = correct_answer(question, current_answer, evaluation, context)
        # Avoid endless loops if the model repeats the same answer.
        if revised.strip() == current_answer.strip():
            break
        current_answer = revised
        evaluation = evaluate(question, current_answer, context)
        history.append({"iteration": attempt + 1, "answer": current_answer,
                        "score": evaluation["score"], "status": evaluation["status"]})

    return {"initial_answer": initial_answer, "final_answer": current_answer,
            "evaluation": evaluation, "history": history}
