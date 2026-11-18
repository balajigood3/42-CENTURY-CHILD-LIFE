"""Local Ollama response generation."""
import json
import urllib.request
import urllib.error
from .assistant import build_prompt, validate_response

def ask_ollama(question, documents, role, model="qwen2.5:3b",
               host="http://localhost:11434", timeout=180):
    prompt = build_prompt(question, documents, role)
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "format": "json", "options": {"temperature": 0.2}}).encode()
    request = urllib.request.Request(host.rstrip("/") + "/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Ollama unavailable. Start Ollama or select offline retrieval mode.") from exc
    try:
        data = json.loads(raw.get("response", ""))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model did not return valid JSON.") from exc
    return validate_response(data, {d["id"] for d in documents})
