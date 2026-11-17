from core.verification import verify_claims
from core.correction import correct_answer

def verify_and_correct(question, answer, knowledge_base, extra_context=""):
    evidence = knowledge_base.search(question + " " + answer)
    if extra_context.strip():
        from core.chunking import chunk_text
        evidence.extend({
            "source": "User-provided context",
            "part": i + 1,
            "text": chunk
        } for i, chunk in enumerate(chunk_text(extra_context)))
    # Cap evidence sent to the local model.
    evidence = evidence[:8]
    claims, summary = verify_claims(question, answer, evidence)

    statuses = {item["status"] for item in claims}
    if not claims:
        overall = "UNKNOWN"
    elif "CONTRADICTED" in statuses:
        overall = "CONTRADICTION FOUND"
    elif "UNKNOWN" in statuses:
        overall = "PARTIALLY VERIFIED / UNKNOWN"
    else:
        overall = "SUPPORTED BY PROVIDED EVIDENCE"

    corrected = correct_answer(question, answer, claims, evidence)
    return {
        "overall_status": overall,
        "summary": summary,
        "claims": claims,
        "corrected_answer": corrected
    }
