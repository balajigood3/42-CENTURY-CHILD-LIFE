from core.llm import ask_json

VERIFY_PROMPT = """Review the proposed solution for relevance, completeness,
internal consistency, and whether it addresses the original problem.
Do not claim external facts are verified without sources. Do not reveal private
chain-of-thought. Return valid JSON:
{"status":"PASS or NEEDS_REVISION", "issues":["..."], "suggestions":["..."],
 "brief_reason":"..."}
Original problem: {problem}
Proposed solution: {solution}
"""

def verify_solution(problem, solution):
    data = ask_json(VERIFY_PROMPT.format(problem=problem, solution=solution))
    status = str(data.get("status", "NEEDS_REVISION")).upper()
    if status not in {"PASS", "NEEDS_REVISION"}:
        status = "NEEDS_REVISION"
    return {
        "status": status,
        "issues": data.get("issues", []),
        "suggestions": data.get("suggestions", []),
        "brief_reason": str(data.get("brief_reason", ""))
    }
