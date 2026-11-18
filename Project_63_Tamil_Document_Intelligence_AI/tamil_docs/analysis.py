"""Language-aware metadata, chunking, search and grounded summaries."""
from __future__ import annotations
import re
from collections import Counter

TAMIL_RE = re.compile(r"[\u0B80-\u0BFF]")
WORD_RE = re.compile(r"[\u0B80-\u0BFF]+|[A-Za-z0-9_]+")

def detect_language(text: str) -> str:
    tamil = len(TAMIL_RE.findall(text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if tamil and latin:
        return "Tamil-English mixed"
    if tamil:
        return "Tamil"
    if latin:
        return "English"
    return "Unknown"

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start, end)
            if boundary > start:
                end = boundary
        chunks.append(cleaned[start:end].strip())
        if end >= len(cleaned):
            break
        start = max(start + 1, end - overlap)
    return [part for part in chunks if part]

def keywords(text: str, limit: int = 12) -> list[str]:
    words = [w.lower() for w in WORD_RE.findall(text) if len(w) > 1]
    stop = {"என்று", "மற்றும்", "ஒரு", "இந்த", "அது", "the", "and", "for", "with", "this", "that"}
    counts = Counter(w for w in words if w not in stop)
    return [word for word, _ in counts.most_common(limit)]

def search_chunks(chunks: list[str], query: str, limit: int = 4) -> list[dict]:
    query_terms = {w.lower() for w in WORD_RE.findall(query) if len(w) > 1}
    if not query_terms:
        return []
    scored = []
    for index, chunk in enumerate(chunks):
        terms = {w.lower() for w in WORD_RE.findall(chunk)}
        score = len(query_terms & terms)
        if score:
            scored.append({"chunk_id": index, "score": score, "text": chunk})
    return sorted(scored, key=lambda x: (-x["score"], x["chunk_id"]))[:limit]

def extractive_summary(text: str, max_sentences: int = 5) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?。])\s+", text.strip()) if s.strip()]
    return "\n".join(f"- {s}" for s in sentences[:max_sentences]) if sentences else "சுருக்கம் உருவாக்க உரை கிடைக்கவில்லை."
