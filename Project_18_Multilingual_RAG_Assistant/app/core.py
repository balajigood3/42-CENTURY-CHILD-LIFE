import json, re
from typing import Iterable

LANGUAGE_HINTS = {
    "ta": "Tamil", "hi": "Hindi", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati",
    "pa": "Punjabi", "ur": "Urdu", "en": "English"
}

def detect_language(text: str) -> str:
    """Lightweight script-based detection for common Indian languages."""
    if re.search(r"[\u0B80-\u0BFF]", text): return "Tamil"
    if re.search(r"[\u0900-\u097F]", text): return "Hindi/Devanagari"
    if re.search(r"[\u0C00-\u0C7F]", text): return "Telugu"
    if re.search(r"[\u0C80-\u0CFF]", text): return "Kannada"
    if re.search(r"[\u0D00-\u0D7F]", text): return "Malayalam"
    if re.search(r"[\u0980-\u09FF]", text): return "Bengali"
    if re.search(r"[\u0A80-\u0AFF]", text): return "Gujarati"
    if re.search(r"[\u0A00-\u0A7F]", text): return "Punjabi"
    if re.search(r"[\u0600-\u06FF]", text): return "Arabic-script language (e.g. Urdu)"
    return "English or Latin-script language"

def chunk_text(text: str, source: str, chunk_size: int = 900, overlap: int = 120) -> list[dict]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text: return []
    chunks, start, index = [], 0, 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = text.rfind(" ", start + chunk_size // 2, end)
            if boundary > start: end = boundary
        part = text[start:end].strip()
        if part:
            chunks.append({"id": f"{source}::chunk_{index}", "source": source,
                           "text": part, "language": detect_language(part)})
            index += 1
        if end >= len(text): break
        start = max(start + 1, end - overlap)
    return chunks

class MultilingualRetriever:
    """Character n-gram TF-IDF works across Unicode scripts without API calls."""
    def __init__(self):
        self.vectorizer = None
        self.matrix = None
        self.chunks = []

    def fit(self, chunks: list[dict]):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.chunks = list(chunks)
        if not self.chunks:
            self.vectorizer = self.matrix = None
            return
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2,5),
                                          min_df=1, sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([c["text"] for c in self.chunks])

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.chunks or not query.strip(): return []
        from sklearn.metrics.pairwise import cosine_similarity
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [{**self.chunks[i], "score": float(scores[i])}
                for i in ranked if scores[i] > 0]

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

def generate_answer(query: str, retrieved: list[dict], client: OllamaClient,
                    answer_language: str = "auto") -> str:
    if answer_language == "auto":
        language = detect_language(query)
    else:
        language = answer_language
    context = "\n\n".join(
        f"[Source: {item['source']} | Chunk: {item['id']}]\n{item['text']}"
        for item in retrieved
    )
    prompt = (
        "You are a multilingual retrieval-augmented assistant. Answer using ONLY the context. "
        "If the context does not contain the answer, say that the provided documents do not "
        "contain enough information. Do not invent facts. Cite source filenames in square brackets. "
        f"Respond in {language}, unless the user explicitly asks for another language.\n\n"
        f"QUESTION:\n{query}\n\nCONTEXT:\n{context or '[No relevant context retrieved]'}"
    )
    return client.generate(prompt)

def format_sources(results: Iterable[dict]) -> list[dict]:
    return [{"source": r["source"], "chunk_id": r["id"],
             "score": round(r["score"], 4), "language": r["language"]}
            for r in results]
