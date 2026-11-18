from __future__ import annotations
import json
import os
import re
import requests
from .schema import Workflow

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

SYSTEM_PROMPT = """You design safe business workflows. Return ONLY valid JSON matching:
{"title":"...","objective":"...","nodes":[{"id":"start","name":"...","action":"...","owner":"...","inputs":[],"outputs":[],"depends_on":[],"on_failure":"..."}]}
Use 3-8 nodes. IDs must be unique, dependencies must refer to earlier logical steps, and the graph must be acyclic.
Do not include executable shell commands, scripts, credentials, or external side effects.
"""

def fallback_workflow(task: str) -> Workflow:
    clean = re.sub(r"\s+", " ", task).strip()
    subject = clean[:90] or "Requested business task"
    raw = {
        "title": f"Workflow: {subject}",
        "objective": clean[:450] or "Complete the requested business task safely.",
        "nodes": [
            {"id":"capture","name":"Capture request","action":"Record the request, desired outcome, constraints, and deadline.","owner":"Requester","inputs":["Task description"],"outputs":["Approved task brief"],"depends_on":[]},
            {"id":"plan","name":"Plan work","action":"Break the task into deliverables, assign owners, and identify dependencies.","owner":"Coordinator","inputs":["Approved task brief"],"outputs":["Work plan"],"depends_on":["capture"]},
            {"id":"prepare","name":"Prepare resources","action":"Collect required information, tools, and approvals; check access and readiness.","owner":"Assigned team","inputs":["Work plan"],"outputs":["Ready resources"],"depends_on":["plan"]},
            {"id":"execute","name":"Perform work","action":"Complete the planned activities and record evidence of each result.","owner":"Assigned team","inputs":["Ready resources"],"outputs":["Completed deliverables"],"depends_on":["prepare"]},
            {"id":"review","name":"Review quality","action":"Check deliverables against acceptance criteria and request corrections if needed.","owner":"Reviewer","inputs":["Completed deliverables","Acceptance criteria"],"outputs":["Review decision"],"depends_on":["execute"]},
            {"id":"close","name":"Close and report","action":"Share the approved outcome, document lessons, and close the task.","owner":"Coordinator","inputs":["Review decision"],"outputs":["Completion report"],"depends_on":["review"]}
        ]
    }
    return Workflow.model_validate(raw)

def _extract_json(content: str) -> dict:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    start, end = content.find("{"), content.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model response did not contain a JSON object")
    return json.loads(content[start:end+1])

def generate_workflow(task: str, use_ollama: bool = True) -> tuple[Workflow, str]:
    if not task or len(task.strip()) < 8:
        raise ValueError("Please describe the task in at least 8 characters.")
    if use_ollama:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "stream": False,
                      "format": "json",
                      "messages":[{"role":"system","content":SYSTEM_PROMPT},
                                 {"role":"user","content":task.strip()}]},
                timeout=90
            )
            response.raise_for_status()
            content = response.json()["message"]["content"]
            workflow = Workflow.model_validate(_extract_json(content))
            return workflow, f"Generated with local Ollama model ({OLLAMA_MODEL})"
        except Exception as exc:
            workflow = fallback_workflow(task)
            return workflow, f"Deterministic fallback used (Ollama unavailable or invalid response: {type(exc).__name__})"
    return fallback_workflow(task), "Deterministic fallback used (local model disabled)"

def to_mermaid(workflow: Workflow) -> str:
    lines = ["flowchart TD"]
    for node in workflow.nodes:
        label = node.name.replace('"', "'").replace("\n", " ")
        lines.append(f'    {node.id}["{label}"]')
    for node in workflow.nodes:
        for dep in node.depends_on:
            lines.append(f"    {dep} --> {node.id}")
    return "\n".join(lines) + "\n"
