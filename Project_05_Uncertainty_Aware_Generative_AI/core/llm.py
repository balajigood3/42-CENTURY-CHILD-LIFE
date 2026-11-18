import json
import requests
from config import OLLAMA_URL, MODEL_NAME, REQUEST_TIMEOUT

def ask_json(prompt):
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False,
               "format": "json", "options": {"temperature": 0.1}}
    response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    raw = response.json().get("response", "").strip()
    if not raw:
        raise ValueError("Local LLM வெற்று பதிலைத் தந்தது.")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM சரியான JSON தரவில்லை: {raw[:400]}") from exc
    if not isinstance(data, dict):
        raise ValueError("LLM JSON object வழங்கவில்லை.")
    return data
