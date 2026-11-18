import json
import re
from datetime import datetime, timezone
from typing import Optional

def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_]+|[\u0B80-\u0BFF]+|[\u0900-\u097F]+|[\u0C00-\u0C7F]+|[\u0C80-\u0CFF]+|[\u0D00-\u0D7F]+", text.lower())

def split_chunks(text: str, source: str, category: str = "general",
                 chunk_size: int = 850, overlap: int = 120) -> list[dict]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start, index = [], 0, 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = text.rfind(" ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary
        part = text[start:end].strip()
        if part:
            chunks.append({
                "chunk_id": f"{source}::chunk_{index}", "source": source,
                "category": category, "text": part, "chunk_index": index,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            index += 1
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks

def expand_query(query: str, history: list[dict], client=None) -> str:
    """Resolve conversational references using recent turns; fall back safely without LLM."""
    if not history:
        return query.strip()
    recent = history[-6:]
    if client is None:
        prior_terms = " ".join(str(t.get("content", "")) for t in recent)
        # Keep the original query intact; prior turns only provide retrieval context.
        return f"{query.strip()} {prior_terms[-500:]}"
    prompt = (
        "Rewrite the latest user query into a standalone search query using only relevant "
        "conversation context. Preserve names, dates, constraints and the original intent. "
        "Do not answer the question. Return only the rewritten query.\n"
        f"RECENT CONVERSATION:\n{json.dumps(recent, ensure_ascii=False)}\n"
        f"LATEST QUERY:\n{query}"
    )
    try:
        result = client.generate(prompt).strip()
        return result[:1000] if result else query.strip()
    except Exception:
        return query.strip()

def lexical_score(query_tokens: set[str], document: str) -> float:
    doc_tokens = set(tokenize(document))
    if not query_tokens:
        return 0.0
    return len(query_tokens & doc_tokens) / len(query_tokens)

def retrieve(query: str, chunks: list[dict], history: Optional[list[dict]] = None,
             category: Optional[str] = None, source: Optional[str] = None,
             top_k: int = 5, client=None) -> list[dict]:
    history = history or []
    expanded = expand_query(query, history, client)
    q_tokens = set(tokenize(expanded))
    original_tokens = set(tokenize(query))
    scored = []
    for item in chunks:
        if category and category != "All" and item.get("category") != category:
            continue
        if source and source != "All" and item.get("source") != source:
            continue
        body = item.get("text", "")
        base = lexical_score(q_tokens, body)
        direct = lexical_score(original_tokens, body)
        # Prefer direct query matches; use conversational context as a smaller signal.
        score = 0.72 * direct + 0.28 * base
        if history:
            history_terms = set(tokenize(" ".join(str(t.get("content","")) for t in history[-4:])))
            score += 0.08 * lexical_score(history_terms, body)
        if score > 0:
            scored.append({**item, "score": round(score, 5), "expanded_query": expanded})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:max(1, top_k)]

class OllamaClient:
    def __init__(self, model="qwen2.5:3b", host="http://localhost:11434"):
        self.model, self.host = model, host.rstrip("/")
    def generate(self, prompt: str) -> str:
        import urllib.request
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False,
                              "options": {"temperature": 0.1}}).encode()
        req = urllib.request.Request(self.host + "/api/generate", data=payload,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return json.loads(response.read().decode())["response"]
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

def answer_query(query: str, results: list[dict], history: list[dict], client: OllamaClient,
                 answer_language: str = "auto") -> str:
    context = "\n\n".join(
        f"[{r['source']} | category={r.get('category','general')} | chunk={r['chunk_id']}]\n{r['text']}"
        for r in results
    )
    recent = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in history[-6:])
    language_rule = "Use the language of the latest user query." if answer_language == "auto" else f"Answer in {answer_language}."
    prompt = (
        "You are a context-aware retrieval assistant. Answer using retrieved document context "
        "and relevant conversation context. Retrieved documents are the factual evidence; "
        "conversation history only resolves references and intent. Do not invent facts. "
        "If evidence is insufficient, say so. Cite source filenames in square brackets. "
        f"{language_rule}\n\nCONVERSATION:\n{recent or '[No prior turns]'}\n\n"
        f"QUESTION:\n{query}\n\nRETRIEVED EVIDENCE:\n{context or '[No relevant passages]'}"
    )
    return client.generate(prompt)
