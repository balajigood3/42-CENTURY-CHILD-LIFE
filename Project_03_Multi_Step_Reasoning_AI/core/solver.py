from core.llm import ask_llm

SOLVER_PROMPT = """You are a careful problem-solving assistant.
Solve only the assigned subtask. Use the original problem, context, and any
previous subtask results provided. State assumptions explicitly. If information
is missing, say what is unknown. Give a concise answer with a short explanation,
not hidden private chain-of-thought.

Original problem:
{problem}

Current subtask:
{task}

Context:
{context}

Previous results:
{previous}

Provide the subtask result.
"""

def solve_subtask(problem, task, context, previous):
    return ask_llm(SOLVER_PROMPT.format(
        problem=problem,
        task=task,
        context=context or "No additional context.",
        previous=previous or "No previous results."
    ))
