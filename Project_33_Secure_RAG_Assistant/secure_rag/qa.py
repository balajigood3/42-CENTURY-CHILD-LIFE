from __future__ import annotations
from .retriever import retrieve

def answer_question(question: str, role: str, top_k: int = 4, db_path=None):
    results = retrieve(question, role, top_k=top_k, db_path=db_path)
    if not results:
        return {
            "answer": "The authorized knowledge base does not contain enough matching information to answer this question.",
            "citations": [],
            "warnings": []
        }
    citations = []
    answer_parts = []
    warnings = []
    for index, item in enumerate(results, 1):
        answer_parts.append(f"[{index}] {item['content']}")
        citations.append({
            "citation": f"[{index}]",
            "document": item["doc_name"],
            "chunk": item["chunk_index"] + 1,
            "score": item["score"]
        })
        if item["contains_suspicious_instruction"]:
            warnings.append(
                f"Suspicious instruction-like text was found in {item['doc_name']} and neutralized before display."
            )
    answer = (
        "Relevant authorized source excerpts:\n\n"
        + "\n\n".join(answer_parts)
        + "\n\nThis is an extractive response. Verify the cited source text before acting."
    )
    return {"answer": answer, "citations": citations, "warnings": warnings}
