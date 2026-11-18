from __future__ import annotations
import json, os, re
import requests
from .models import GoalPlan

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

SYSTEM_PROMPT = """You are a practical goal planning assistant. Return only valid JSON:
{"goal":"...","deadline_days":30,"assumptions":["..."],"milestones":["..."],"tasks":[{"id":"T01","title":"...","description":"...","milestone":"...","priority":"High","estimated_days":2,"depends_on":[],"success_criteria":"..."}]}
Create 4-10 realistic tasks, use unique IDs T01, T02..., refer only to existing task IDs in depends_on, and make the dependency graph acyclic. Keep total estimated task days within the deadline where practical. Do not claim certainty about external outcomes.
"""

def fallback_plan(goal: str, deadline_days: int) -> GoalPlan:
    goal = re.sub(r"\s+", " ", goal).strip()
    milestones = ["Define and prepare", "Execute core work", "Review and complete"]
    raw = {
        "goal": goal,
        "deadline_days": deadline_days,
        "assumptions": [
            "The user can access the resources required for the goal.",
            "The deadline is a planning target, not a guarantee of completion."
        ],
        "milestones": milestones,
        "tasks": [
            {"id":"T01","title":"Define the outcome","description":"Write a measurable definition of success and identify constraints.","milestone":milestones[0],"priority":"High","estimated_days":1,"depends_on":[],"success_criteria":"A clear, measurable success statement is documented."},
            {"id":"T02","title":"Assess resources","description":"List available time, skills, tools, budget, and support; identify gaps.","milestone":milestones[0],"priority":"High","estimated_days":2,"depends_on":["T01"],"success_criteria":"Required resources and gaps are documented."},
            {"id":"T03","title":"Create an action plan","description":"Break the goal into manageable tasks and schedule them against the deadline.","milestone":milestones[0],"priority":"High","estimated_days":1,"depends_on":["T02"],"success_criteria":"A dated task plan with priorities is ready."},
            {"id":"T04","title":"Complete the first work block","description":"Perform the highest-priority initial tasks and record evidence of progress.","milestone":milestones[1],"priority":"High","estimated_days":max(1, deadline_days//4),"depends_on":["T03"],"success_criteria":"The first planned deliverable is completed and recorded."},
            {"id":"T05","title":"Execute remaining work","description":"Complete the remaining planned tasks, updating estimates and blockers as needed.","milestone":milestones[1],"priority":"High","estimated_days":max(1, deadline_days//2),"depends_on":["T04"],"success_criteria":"All planned core deliverables are completed."},
            {"id":"T06","title":"Review and adjust","description":"Compare results with success criteria, resolve gaps, and revise the plan if required.","milestone":milestones[2],"priority":"Medium","estimated_days":2,"depends_on":["T05"],"success_criteria":"Outstanding gaps are resolved or explicitly documented."},
            {"id":"T07","title":"Confirm completion","description":"Verify the outcome, summarize evidence, and capture lessons for future goals.","milestone":milestones[2],"priority":"Medium","estimated_days":1,"depends_on":["T06"],"success_criteria":"A completion summary is approved by the goal owner."}
        ]
    }
    return GoalPlan.model_validate(raw)

def _extract_json(content: str) -> dict:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    start, end = content.find("{"), content.rfind("}")
    if start < 0 or end < start:
        raise ValueError("No JSON object in model response")
    return json.loads(content[start:end+1])

def create_plan(goal: str, deadline_days: int, use_ollama: bool = True):
    if len(goal.strip()) < 8:
        raise ValueError("Please describe the goal in at least 8 characters.")
    if not 1 <= int(deadline_days) <= 3650:
        raise ValueError("Deadline must be between 1 and 3650 days.")
    if use_ollama:
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model":OLLAMA_MODEL,"stream":False,"format":"json",
                      "messages":[{"role":"system","content":SYSTEM_PROMPT},
                                 {"role":"user","content":f"Goal: {goal.strip()}\nDeadline in days: {deadline_days}"}]},
                timeout=90
            )
            response.raise_for_status()
            plan = GoalPlan.model_validate(_extract_json(response.json()["message"]["content"]))
            return plan, f"Local Ollama model: {OLLAMA_MODEL}"
        except Exception as exc:
            return fallback_plan(goal, deadline_days), f"Fallback plan used ({type(exc).__name__})"
    return fallback_plan(goal, deadline_days), "Deterministic fallback plan (LLM disabled)"

def progress_summary(plan: GoalPlan, completed_ids: set[str]) -> dict:
    known = {t.id for t in plan.tasks}
    completed = completed_ids & known
    remaining = known - completed
    percent = round((len(completed) / len(known)) * 100) if known else 0
    blocked = [t.id for t in plan.tasks if t.id in remaining and any(d in remaining for d in t.depends_on)]
    ready = [t.id for t in plan.tasks if t.id in remaining and all(d in completed for d in t.depends_on)]
    return {"completed":len(completed),"total":len(known),"percent":percent,
            "remaining":len(remaining),"ready":ready,"blocked":blocked}
