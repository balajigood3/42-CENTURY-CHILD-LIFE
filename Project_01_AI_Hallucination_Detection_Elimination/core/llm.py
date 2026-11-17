import json
import requests
from config import OLLAMA_URL, MODEL_NAME, REQUEST_TIMEOUT

def generate(prompt: str, temperature: float = 0.1) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature}
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    text = response.json().get("response", "").strip()
    if not text:
        raise ValueError("Local LLM வெற்று பதிலைத் தந்தது.")
    return text

def generate_json(prompt: str) -> dict:
    raw = generate(prompt)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # One constrained repair attempt; never silently trust malformed output.
        repair = f"""Convert the following content into valid JSON only.
Use this schema:
{{"claims":[],"summary":"","corrected_answer":""}}
Do not add facts. Content:
{raw}"""
        repaired = generate(repair, temperature=0)
        return json.loads(repaired)
