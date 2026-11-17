import requests
from config import OLLAMA_URL, MODEL_NAME, REQUEST_TIMEOUT

def generate(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    answer = response.json().get("response", "").strip()
    if not answer:
        raise ValueError("Local LLM வெற்று பதிலைத் தந்தது.")
    return answer
