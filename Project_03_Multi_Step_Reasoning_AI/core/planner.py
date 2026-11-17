from core.llm import ask_json

PLANNER_PROMPT = """You are a task planner. Break the user's problem into a small,
ordered list of independent or sequential subtasks. Do not provide private chain
of thought. Return only concise task descriptions and a short problem summary.
Return valid JSON:
{"problem_summary":"...", "steps":[{"task":"..."}]}
Create between 2 and {max_steps} steps. Avoid duplicate tasks.
Problem: {problem}
Context: {context}
"""

def create_plan(problem: str, context: str, max_steps: int) -> dict:
    data = ask_json(PLANNER_PROMPT.format(
        max_steps=max_steps,
        problem=problem,
        context=context or "No additional context."
    ))
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        raise ValueError("Planner output-ல் steps பட்டியல் இல்லை.")
    cleaned = []
    for item in steps[:max_steps]:
        if isinstance(item, dict) and str(item.get("task", "")).strip():
            cleaned.append({"task": str(item["task"]).strip()})
    if len(cleaned) < 2:
        raise ValueError("Planner குறைந்தது இரண்டு செல்லுபடியான துணைப் பணிகளை உருவாக்க வேண்டும்.")
    return {
        "problem_summary": str(data.get("problem_summary", "சிக்கல் சுருக்கம் கிடைக்கவில்லை.")),
        "steps": cleaned
    }
