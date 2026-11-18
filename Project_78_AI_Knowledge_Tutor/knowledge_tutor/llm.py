"""Local Ollama integration for knowledge tutoring."""
import json
import urllib.request
import urllib.error
from .tutor import build_prompt, validate_tutor_output

def generate_tutor_output(topic, learner_level, question, reference_notes="",
                          lesson_length="Detailed", model="qwen2.5:3b",
                          host="http://localhost:11434", timeout=180):
    prompt = build_prompt(topic, learner_level, question, reference_notes, lesson_length)
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "format": "json", "options": {"temperature": 0.2}}).encode()
    req = urllib.request.Request(host.rstrip("/") + "/api/generate", data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Ollama unavailable. Start Ollama or select Offline study scaffold.") from exc
    try:
        result = json.loads(raw.get("response", ""))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model did not return valid JSON. Please retry.") from exc
    return validate_tutor_output(result)
