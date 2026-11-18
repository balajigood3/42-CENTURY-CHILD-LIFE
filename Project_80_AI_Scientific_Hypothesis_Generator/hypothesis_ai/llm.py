"""Local Ollama adapter."""
import json
import urllib.request
import urllib.error
from .generator import build_prompt, validate_output

def generate_hypotheses(field, observation, background, study_type, constraints="",
                        model="qwen2.5:3b", host="http://localhost:11434", timeout=240):
    prompt = build_prompt(field, observation, background, study_type, constraints)
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "format": "json", "options": {"temperature": 0.2}}).encode()
    request = urllib.request.Request(host.rstrip("/") + "/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Ollama unavailable. Start Ollama or choose Offline template mode.") from exc
    try:
        result = json.loads(raw.get("response", ""))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model did not return valid JSON. Retry or select another model.") from exc
    return validate_output(result)
