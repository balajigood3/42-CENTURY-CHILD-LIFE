from __future__ import annotations
import json
import urllib.request
import urllib.error
from .normalizer import normalize_code_mixed, detect_script_mix

def offline_reply(text: str) -> str:
    normalized = normalize_code_mixed(text)
    q = normalized.lower()
    if any(x in q for x in ("வணக்கம்", "hello", "hi")):
        return "வணக்கம்! தமிழிலும் English mix செய்தும் கேள்விகள் கேட்கலாம்."
    if "ai என்றால் என்ன" in q or "artificial intelligence" in q:
        return "AI (செயற்கை நுண்ணறிவு) என்பது மனித அறிவாற்றலை ஒத்த பணிகளை கணினி அமைப்புகள் செய்ய உதவும் தொழில்நுட்பம்."
    if "rag என்றால் என்ன" in q or "rag" == q.strip():
        return "RAG (Retrieval-Augmented Generation) என்பது ஆவணங்களில் இருந்து தொடர்புடைய தகவலைத் தேடி, அதன் அடிப்படையில் LLM பதில் உருவாக்கும் முறை."
    if "எப்படி செயல்படும்" in q:
        return "முதலில் input புரிந்துகொள்ளப்படும்; பின்னர் தொடர்புடைய தகவல் அல்லது விதிகள் பயன்படுத்தப்பட்டு பதில் உருவாக்கப்படும்."
    return ("இந்தக் கேள்விக்கு offline demo-வில் பொருத்தமான பதில் இல்லை. "
            "விரிவான code-mixed புரிதலுக்கு local Ollama model பயன்படுத்தவும்.")

def local_llm_reply(text: str, model: str = "qwen2.5:3b",
                    base_url: str = "http://localhost:11434") -> str:
    normalized = normalize_code_mixed(text)
    prompt = (
        "You are a helpful Tamil-English code-mixed assistant. Understand Tamil written "
        "in Tamil script and romanized Tamil mixed with English. Reply naturally in the "
        "same style as the user, primarily Tamil. If unsure, say so; do not invent facts.\n\n"
        f"User: {text}\nNormalized hint: {normalized}\nAssistant:"
    )
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = payload.get("response", "").strip()
        if not result:
            raise RuntimeError("Local model returned an empty response.")
        return result
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama connection failed: {exc}") from exc

def answer(text: str, use_local: bool = False, model: str = "qwen2.5:3b") -> dict:
    if not text.strip():
        raise ValueError("கேள்வியை உள்ளிடுங்கள்.")
    response = local_llm_reply(text, model) if use_local else offline_reply(text)
    return {"answer": response, "script_mix": detect_script_mix(text),
            "normalized_hint": normalize_code_mixed(text)}
