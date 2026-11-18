from __future__ import annotations
import json, os, re
import requests
from .models import TaskBreakdown

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

SYSTEM_PROMPT = """You are a project task decomposition specialist. Return ONLY JSON:
{"project":"...","objective":"...","assumptions":["..."],"subtasks":[{"id":"S01","title":"...","description":"...","parent_id":null,"priority":"High","estimated_hours":2,"depends_on":[],"deliverable":"...","acceptance_criteria":"..."}]}
Create 5-12 actionable subtasks. IDs must be unique in S01 format. Dependencies must refer to existing IDs and be acyclic. parent_id is optional and must refer to another existing subtask. Avoid executable commands, credentials, or external side effects. Estimates are approximate hours.
"""

def fallback_breakdown(task: str) -> TaskBreakdown:
    project = re.sub(r"\s+", " ", task).strip()
    raw = {
        "project": project[:155],
        "objective": project[:450],
        "assumptions": [
            "The requester will confirm scope, constraints, and acceptance criteria.",
            "Time estimates are indicative and should be adjusted by the delivery team."
        ],
        "subtasks": [
            {"id":"S01","title":"Clarify scope and outcome","description":"Confirm the intended outcome, boundaries, stakeholders, and constraints.","priority":"Critical","estimated_hours":2,"depends_on":[],"deliverable":"Approved task brief","acceptance_criteria":"Outcome, scope, constraints, and stakeholders are documented."},
            {"id":"S02","title":"Identify requirements","description":"Gather functional, non-functional, and operational requirements.","priority":"High","estimated_hours":3,"depends_on":["S01"],"deliverable":"Requirements list","acceptance_criteria":"Requirements are clear, testable, and prioritized."},
            {"id":"S03","title":"Break down solution design","description":"Identify components, resources, interfaces, and implementation approach.","priority":"High","estimated_hours":4,"depends_on":["S02"],"deliverable":"Solution outline","acceptance_criteria":"Components and their responsibilities are described."},
            {"id":"S04","title":"Prepare resources and environment","description":"Confirm access, tools, data, people, and working environment readiness.","priority":"Medium","estimated_hours":2,"depends_on":["S03"],"deliverable":"Readiness checklist","acceptance_criteria":"Required resources are available or gaps have owners."},
            {"id":"S05","title":"Implement core work","description":"Complete the main implementation in small, reviewable increments.","priority":"High","estimated_hours":8,"depends_on":["S04"],"deliverable":"Core implementation","acceptance_criteria":"Core requirements are implemented and demonstrable."},
            {"id":"S06","title":"Validate and test","description":"Test the result against requirements and record defects or gaps.","priority":"High","estimated_hours":4,"depends_on":["S05"],"deliverable":"Test evidence","acceptance_criteria":"Critical acceptance checks pass or exceptions are documented."},
            {"id":"S07","title":"Review and refine","description":"Resolve review feedback and improve quality, usability, and completeness.","priority":"Medium","estimated_hours":3,"depends_on":["S06"],"deliverable":"Reviewed deliverable","acceptance_criteria":"Review comments are addressed or assigned."},
            {"id":"S08","title":"Document and hand over","description":"Prepare usage notes, decisions, known limitations, and handover summary.","priority":"Low","estimated_hours":2,"depends_on":["S07"],"deliverable":"Handover package","acceptance_criteria":"A recipient can understand and use the completed deliverable."}
        ]
    }
    return TaskBreakdown.model_validate(raw)

def _extract_json(content: str) -> dict:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    start, end = content.find("{"), content.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object found in model response")
    return json.loads(content[start:end+1])

def decompose_task(task: str, use_ollama: bool = True):
    if len(task.strip()) < 8:
        raise ValueError("Describe the task in at least 8 characters.")
    if use_ollama:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model":OLLAMA_MODEL,"stream":False,"format":"json",
                      "messages":[{"role":"system","content":SYSTEM_PROMPT},
                                 {"role":"user","content":task.strip()}]},
                timeout=90
            )
            response.raise_for_status()
            breakdown = TaskBreakdown.model_validate(_extract_json(response.json()["message"]["content"]))
            return breakdown, f"Generated with local Ollama model ({OLLAMA_MODEL})"
        except Exception as exc:
            return fallback_breakdown(task), f"Fallback decomposition used ({type(exc).__name__})"
    return fallback_breakdown(task), "Deterministic fallback used (LLM disabled)"

def to_mermaid(breakdown: TaskBreakdown) -> str:
    lines = ["flowchart TD"]
    for item in breakdown.subtasks:
        label = item.title.replace('"', "'").replace("\n", " ")
        lines.append(f'    {item.id}["{label}"]')
    for item in breakdown.subtasks:
        for dep in item.depends_on:
            lines.append(f"    {dep} --> {item.id}")
    return "\n".join(lines) + "\n"
