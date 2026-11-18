"""Tamil-first assistant with deterministic offline mode and optional local Ollama."""
from __future__ import annotations
import json
import urllib.request
import urllib.error

RULES = [
    (("வணக்கம்", "ஹலோ", "hello", "hi"), "வணக்கம்! என்ன உதவி தேவை?"),
    (("நன்றி", "thanks", "thank you"), "உங்களுக்கு உதவ முடிந்ததில் மகிழ்ச்சி."),
    (("உங்கள் பெயர்", "உன் பெயர்", "who are you"), "நான் தமிழ் LLM Assistant. தமிழில் கேள்விகளுக்கு பதிலளிக்க உதவும் உள்ளூர் உதவியாளர்."),
    (("செயற்கை நுண்ணறிவு", "artificial intelligence", "ai என்றால்"), "செயற்கை நுண்ணறிவு (AI) என்பது மனித அறிவாற்றலைப் போன்ற பணிகளை கணினி அமைப்புகள் செய்ய உதவும் தொழில்நுட்பத் துறை."),
    (("இயந்திரக் கற்றல்", "machine learning", "ml என்றால்"), "இயந்திரக் கற்றல் (ML) என்பது தரவிலிருந்து வடிவ-pattern-களை கற்று கணிப்புகள் அல்லது முடிவுகளை உருவாக்கும் AI துணைத்துறை."),
    (("ஜெனரேட்டிவ் ai", "generative ai", "உருவாக்கும் செயற்கை நுண்ணறிவு"), "Generative AI என்பது உரை, படம், ஒலி, குறியீடு போன்ற புதிய உள்ளடக்கங்களை உருவாக்கும் மாதிரிகளைக் குறிக்கிறது."),
    (("rag என்றால்", "retrieval augmented generation"), "RAG என்பது வெளிப்புற ஆவணங்கள் அல்லது அறிவுத் தரவிலிருந்து தொடர்புடைய தகவலை மீட்டெடுத்து, அதன் அடிப்படையில் LLM பதில் உருவாக்கும் அணுகுமுறை."),
]

def offline_answer(question: str) -> str:
    q = question.strip().lower()
    if not q:
        return "தயவுசெய்து ஒரு கேள்வியை உள்ளிடுங்கள்."
    for keys, answer in RULES:
        if any(key in q for key in keys):
            return answer
    return ("இந்தக் கேள்விக்கு offline demo-வில் உறுதிப்படுத்தப்பட்ட பதில் இல்லை. "
            "மேலும் விரிவான பதிலுக்கு Ollama-வில் உள்ளூர் மொழி மாதிரியை இயக்கி மீண்டும் முயற்சிக்கவும். "
            "முக்கிய தகவல்களை நம்பகமான ஆதாரங்களுடன் சரிபார்க்கவும்.")

def ollama_answer(question: str, model: str = "qwen2.5:3b",
                  base_url: str = "http://localhost:11434") -> str:
    """Call a local Ollama server; no cloud API key is used."""
    prompt = (
        "நீங்கள் தெளிவாகவும் மரியாதையாகவும் பதிலளிக்கும் தமிழ் உதவியாளர். "
        "பயனர் வேறு மொழி கேட்டால் அந்த மொழியில் பதிலளிக்கலாம். "
        "தெரியாததைத் தெரியாது என்று கூறுங்கள்; உண்மைகளை உருவாக்க வேண்டாம்.\n\n"
        f"கேள்வி: {question}\nபதில்:"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        base_url.rstrip("/") + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data.get("response", "").strip()
        if not answer:
            raise RuntimeError("Local model returned an empty response.")
        return answer
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama connection failed: {exc}") from exc
