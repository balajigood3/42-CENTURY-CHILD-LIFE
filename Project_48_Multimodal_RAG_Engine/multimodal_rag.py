"""Lightweight text + image-OCR RAG engine using local lexical retrieval."""
from __future__ import annotations
import re
from pathlib import Path
from collections import Counter
from PIL import Image
import io

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}
STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "from", "what", "when",
    "where", "which", "who", "how", "are", "was", "were", "you", "your",
    "about", "into", "does", "can", "have", "has"
}

def validate_upload(filename: str, size: int) -> None:
    if Path(filename).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type.")
    if size <= 0:
        raise ValueError("The uploaded file is empty.")
    if size > MAX_UPLOAD_BYTES:
        raise ValueError("Each file must be 20 MB or smaller.")

def extract_image_text(image_bytes: bytes) -> str:
    """OCR an image with optional pytesseract; no OCR model is bundled."""
    try:
        import pytesseract
    except ImportError as exc:
        raise RuntimeError(
            "Image OCR is optional. Install pytesseract and the Tesseract OCR system package."
        ) from exc
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise RuntimeError(f"Could not OCR image: {exc}") from exc

def chunk_text(text: str, source: str = "text", chunk_size: int = 700,
               overlap: int = 100) -> list[dict]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size >= 1 and 0 <= overlap < chunk_size.")
    clean = re.sub(r"\s+", " ", text or "").strip()
    if not clean:
        return []
    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(clean), step):
        part = clean[start:start + chunk_size].strip()
        if part:
            chunks.append({"source": source, "text": part, "chunk_id": len(chunks)})
    return chunks

def build_index(documents: list[dict]) -> list[dict]:
    """Validate and return normalized chunks; retrieval is computed per query."""
    normalized = []
    for item in documents:
        if not isinstance(item, dict) or not item.get("text", "").strip():
            continue
        normalized.append({
            "source": str(item.get("source", "unknown")),
            "text": str(item["text"]),
            "chunk_id": int(item.get("chunk_id", len(normalized))),
        })
    return normalized

def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z0-9_'-]+", text.lower())
            if len(w) > 1 and w not in STOPWORDS]

def retrieve(query: str, chunks: list[dict], top_k: int = 4) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("Question cannot be empty.")
    if top_k < 1 or top_k > 20:
        raise ValueError("top_k must be between 1 and 20.")
    query_tokens = set(_tokens(query))
    scored = []
    for chunk in chunks:
        text_tokens = _tokens(chunk.get("text", ""))
        counts = Counter(text_tokens)
        score = sum(counts[token] for token in query_tokens)
        if score:
            scored.append({**chunk, "score": score})
    scored.sort(key=lambda x: (-x["score"], x["source"], x["chunk_id"]))
    return scored[:top_k]

def answer_with_context(question: str, hits: list[dict]) -> dict:
    if not question.strip():
        raise ValueError("Question cannot be empty.")
    if not hits:
        return {
            "answer": "The indexed sources do not contain a clear matching passage. Try different keywords or add relevant documents.",
            "sources": [],
        }
    excerpts = [hit["text"] for hit in hits[:3]]
    answer = "Based only on the retrieved source passages:\n\n" + "\n\n".join(
        f"- {excerpt}" for excerpt in excerpts
    )
    return {"answer": answer, "sources": hits}
