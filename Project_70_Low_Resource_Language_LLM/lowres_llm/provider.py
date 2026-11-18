"""Provider adapter: local Ollama only; no hosted API key required."""
import json
import urllib.request
import urllib.error
from .prompting import build_prompt

def generate(text: str, language: str, task: str,
             context: str = "", model: str = "qwen2.5:3b",
             host: str = "http://localhost:11434", timeout: int = 120) -> str:
    prompt = build_prompt(text, language, task, context)
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.2}
    }).encode("utf-8")
    request = urllib.request.Request(
        host.rstrip("/") + "/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama server is unavailable. Start Ollama and pull the selected local model."
        ) from exc
    output = data.get("message", {}).get("content", "").strip()
    if not output:
        raise RuntimeError("The local model returned an empty response.")
    return output
