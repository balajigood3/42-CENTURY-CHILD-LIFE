from __future__ import annotations
import re
from collections import Counter
from .store import get_authorized_chunks
from .security import sanitize_untrusted_text, contains_injection

STOPWORDS = {
    "the","a","an","is","are","was","were","to","of","in","on","for","and","or",
    "what","how","when","where","who","which","can","could","please","explain","tell","me"
}

def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-Z0-9_]+", text.lower()) if t not in STOPWORDS and len(t) > 1]

def retrieve(question: str, role: str, top_k: int = 4, db_path=None):
    if not question.strip():
        return []
    if role not in {"admin", "staff", "user"}:
        raise ValueError("Invalid role")
    chunks = get_authorized_chunks(role, db_path) if db_path else get_authorized_chunks(role)
    q_tokens = set(tokens(question))
    ranked = []
    for chunk in chunks:
        content_tokens = tokens(chunk["content"])
        counts = Counter(content_tokens)
        overlap = sum(counts[t] for t in q_tokens)
        if overlap == 0:
            continue
        score = overlap / max(1, len(content_tokens)) ** 0.5
        raw_content = chunk["content"]
        flagged = contains_injection(raw_content)
        safe_content = sanitize_untrusted_text(raw_content)
        ranked.append({
            "id": chunk["id"],
            "doc_name": chunk["doc_name"],
            "chunk_index": chunk["chunk_index"],
            "content": safe_content,
            "score": round(score, 4),
            "contains_suspicious_instruction": flagged
        })
    ranked.sort(key=lambda item: (-item["score"], item["doc_name"], item["chunk_index"]))
    return ranked[:max(1, min(int(top_k), 10))]
