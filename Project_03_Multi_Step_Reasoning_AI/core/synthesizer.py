from core.llm import ask_llm

SYNTHESIS_PROMPT = """Combine the subtask results into one clear, coherent answer.
Address the original problem directly. Resolve obvious inconsistencies, identify
assumptions and limitations, and do not invent missing facts. Provide a concise
solution and a short explanation of the approach, not hidden private chain-of-thought.

Original problem:
{problem}

Context:
{context}

Subtask results:
{results}

Produce the final answer.
"""

def synthesize(problem, context, results):
    return ask_llm(SYNTHESIS_PROMPT.format(
        problem=problem,
        context=context or "No additional context.",
        results=results
    ))
