from core.llm import generate_json

VERIFY_PROMPT = """You are a cautious claim verification assistant.
Break the supplied answer into atomic factual claims. For each claim, compare ONLY
against the supplied evidence. Similarity is not proof. If evidence does not directly
support or contradict the claim, use UNKNOWN. Do not use outside knowledge.
Statuses must be SUPPORTED, CONTRADICTED, or UNKNOWN.
Return JSON only using this schema:
{
 "claims":[{"claim":"...", "status":"SUPPORTED|CONTRADICTED|UNKNOWN",
 "reason":"...", "evidence_indices":[0]}],
 "summary":"short overall assessment"
}
Question: {question}
Answer: {answer}
Evidence:
{evidence}
"""

def verify_claims(question, answer, evidence):
    evidence_text = "\n".join(
        f'[{i}] Source={item["source"]}; Part={item["part"]}; Text={item["text"]}'
        for i, item in enumerate(evidence)
    ) or "NO REFERENCE EVIDENCE PROVIDED."
    result = generate_json(VERIFY_PROMPT.format(
        question=question, answer=answer, evidence=evidence_text
    ))
    verified = []
    for claim in result.get("claims", []):
        status = claim.get("status", "UNKNOWN")
        if status not in {"SUPPORTED", "CONTRADICTED", "UNKNOWN"}:
            status = "UNKNOWN"
        citations = []
        for index in claim.get("evidence_indices", []):
            if isinstance(index, int) and 0 <= index < len(evidence):
                citations.append(evidence[index])
        verified.append({
            "claim": str(claim.get("claim", "")),
            "status": status,
            "reason": str(claim.get("reason", "")),
            "evidence": citations
        })
    return verified, str(result.get("summary", "சுருக்கம் கிடைக்கவில்லை."))
