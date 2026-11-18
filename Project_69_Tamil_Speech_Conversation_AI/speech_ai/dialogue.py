"""Tamil conversation response generation via a local Ollama model."""
from __future__ import annotations
import json
import urllib.request
import urllib.error

SYSTEM_PROMPT = (
    "நீங்கள் தெளிவாகவும் மரியாதையாகவும் தமிழில் பதிலளிக்கும் உரையாடல் உதவியாளர். "
    "பயனர் வேறு மொழியில் கேட்டால் அந்த மொழியில் பதிலளிக்கலாம். "
    "தெரியாத தகவலை கற்பனை செய்து கூற வேண்டாம். பதிலைச் சுருக்கமாகவும் பயனுள்ளதாகவும் அமைக்கவும்."
)

def build_messages(user_text: str, history: list[dict] | None = None) -> list[dict]:
    if not user_text.strip():
        raise ValueError("உரையாடல் உரையை உள்ளிடவும்.")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in (history or [])[-8:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            messages.append({"role": role, "content": content[:4000]})
    messages.append({"role": "user", "content": user_text.strip()})
    return messages

def chat_local(user_text: str, history: list[dict] | None = None,
               model: str = "qwen2.5:3b",
               host: str = "http://localhost:11434", timeout: int = 120) -> str:
    payload = json.dumps({
        "model": model, "messages": build_messages(user_text, history),
        "stream": False
    }).encode("utf-8")
    request = urllib.request.Request(
        host.rstrip("/") + "/api/chat", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama server கிடைக்கவில்லை. Ollama இயங்குகிறதா, model pull செய்யப்பட்டுள்ளதா எனச் சரிபார்க்கவும்."
        ) from exc
    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError("Local model காலியான பதிலை வழங்கியது.")
    return answer
