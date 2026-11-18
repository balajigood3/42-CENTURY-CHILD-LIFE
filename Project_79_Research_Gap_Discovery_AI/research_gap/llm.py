"""Ollama adapter for candidate research-gap analysis."""
import json
import urllib.request
import urllib.error
from .analyzer import build_prompt, validate_analysis

def analyze_research(field, research_question, literature_notes, constraints="",
                    model="qwen2.5:3b", host="http://localhost:11434", timeout=240):
    prompt = build_prompt(field, research_question, literature_notes, constraints)
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "format": "json", "options": {"temperature": 0.1}}).encode()
    request = urllib.request.Request(host.rstrip("/") + "/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError("Ollama unavailable. Start Ollama or choose Offline analysis.") from exc
    try:
        result = json.loads(raw.get("response", ""))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Model did not return valid JSON. Retry or use a different model.") from exc
    return validate_analysis(result)
