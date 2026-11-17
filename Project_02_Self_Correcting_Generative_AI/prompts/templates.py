GENERATION_PROMPT = """You are a careful AI assistant.
Answer the question accurately and clearly.
Use the supplied context when relevant. Do not invent facts.
If the available information is insufficient, explicitly say so.

Question:
{question}

Context:
{context}

Answer:"""

EVALUATION_PROMPT = """Act as a strict answer-quality evaluator.
Compare the answer with the question and supplied context.
Check relevance, completeness, internal consistency, and support from context.
Do not claim that a statement is factually verified merely because it sounds plausible.
If no reference context is supplied, say factual correctness cannot be independently verified.

Question:
{question}

Answer:
{answer}

Context:
{context}

Return exactly:
SCORE: integer from 0 to 100
STATUS: PASS or FAIL
ISSUES: concise list, or None
SUGGESTIONS: concise list, or None
LIMITATION: what cannot be verified
"""

CORRECTION_PROMPT = """Improve the answer using the evaluator feedback.
Preserve correct content. Fix identified issues.
Do not add unsupported facts. If evidence is insufficient, say so clearly.
Return only the revised answer.

Question:
{question}

Previous answer:
{answer}

Evaluation:
{evaluation}

Context:
{context}
"""
