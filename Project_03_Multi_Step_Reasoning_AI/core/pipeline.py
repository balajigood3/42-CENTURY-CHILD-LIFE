from core.planner import create_plan
from core.solver import solve_subtask
from core.synthesizer import synthesize
from core.verifier import verify_solution
from core.llm import ask_llm

REVISION_PROMPT = """Revise this proposed solution using the review feedback.
Do not invent missing facts. Clearly state assumptions and limitations.
Do not provide hidden chain-of-thought.
Problem: {problem}
Current solution: {solution}
Review: {review}
Return the revised final answer.
"""

def solve_problem(problem, context="", max_steps=5, max_revisions=1):
    plan = create_plan(problem, context, max_steps)
    solved = []
    for item in plan["steps"]:
        previous = "\n\n".join(
            f'Task: {x["task"]}\nResult: {x["answer"]}' for x in solved
        )
        answer = solve_subtask(problem, item["task"], context, previous)
        solved.append({"task": item["task"], "answer": answer, "status": "COMPLETED"})

    results_text = "\n\n".join(
        f'Task: {x["task"]}\nAnswer: {x["answer"]}' for x in solved
    )
    final_answer = synthesize(problem, context, results_text)
    review = verify_solution(problem, final_answer)

    for _ in range(max_revisions):
        if review["status"] == "PASS":
            break
        feedback = (
            f'Issues: {review["issues"]}\n'
            f'Suggestions: {review["suggestions"]}\n'
            f'Reason: {review["brief_reason"]}'
        )
        final_answer = ask_llm(REVISION_PROMPT.format(
            problem=problem, solution=final_answer, review=feedback
        ))
        review = verify_solution(problem, final_answer)

    return {
        "problem_summary": plan["problem_summary"],
        "steps": solved,
        "final_answer": final_answer,
        "verification": review
    }
