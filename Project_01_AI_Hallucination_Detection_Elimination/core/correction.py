from core.llm import generate_json

CORRECTION_PROMPT = """Rewrite the answer using only the supplied evidence.
Do not retain claims marked CONTRADICTED. For UNKNOWN claims, either omit them or
clearly state that the supplied sources do not establish them. Do not add new facts.
Return JSON only: {"corrected_answer":"..."}
Question: {question}
Original answer: {answer}
Verification report: {report}
Evidence: {evidence}
"""

def correct_answer(question, answer, claims, evidence):
    report = "\n".join(
        f'{c["status"]}: {c["claim"]} — {c["reason"]}' for c in claims
    )
    evidence_text = "\n".join(
        f'[{i}] {e["source"]}: {e["text"]}' for i, e in enumerate(evidence)
    ) or "No evidence supplied."
    result = generate_json(CORRECTION_PROMPT.format(
        question=question, answer=answer, report=report, evidence=evidence_text
    ))
    return str(result.get("corrected_answer", "ஆதாரங்கள் போதுமானதாக இல்லை."))
