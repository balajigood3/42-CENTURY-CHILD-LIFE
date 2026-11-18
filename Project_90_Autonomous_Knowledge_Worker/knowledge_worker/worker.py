"""Bounded, auditable local knowledge-work planning and execution."""
from __future__ import annotations
import re
from datetime import datetime, timezone

ALLOWED_ACTIONS = {"summarize", "extract", "classify", "draft", "checklist"}

def _clean_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string.")
    return value.strip()

def build_plan(goal, documents, actions):
    goal = _clean_text(goal, "Goal")
    if not isinstance(documents, list) or not documents:
        raise ValueError("Provide at least one knowledge document.")
    cleaned_docs = []
    for idx, doc in enumerate(documents, 1):
        if not isinstance(doc, dict):
            raise ValueError(f"Document {idx} must be an object.")
        title = _clean_text(doc.get("title"), f"Document {idx} title")
        content = _clean_text(doc.get("content"), f"Document {idx} content")
        cleaned_docs.append({"title": title, "content": content})
    if not isinstance(actions, list) or not actions:
        raise ValueError("Select at least one action.")
    if len(actions) != len(set(actions)) or any(a not in ALLOWED_ACTIONS for a in actions):
        raise ValueError(f"Actions must be unique and selected from: {', '.join(sorted(ALLOWED_ACTIONS))}.")
    steps = []
    for action in actions:
        steps.append({
            "step": len(steps) + 1,
            "action": action,
            "description": {
                "summarize": "Create concise summaries of each source.",
                "extract": "Extract key facts, dates, names and figures.",
                "classify": "Assign a broad topic label to each source.",
                "draft": "Draft a response to the stated goal using source evidence.",
                "checklist": "Create actionable tasks grounded in the sources."
            }[action],
            "status": "planned"
        })
    return {
        "goal": goal,
        "documents": cleaned_docs,
        "plan": steps,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "safety": "Only supplied text is processed. No shell, network, email or external actions are executed."
    }

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]

def execute_plan(plan):
    if not isinstance(plan, dict) or not isinstance(plan.get("plan"), list):
        raise ValueError("Invalid plan.")
    docs = plan.get("documents", [])
    if not docs:
        raise ValueError("Plan contains no documents.")
    outputs = []
    for step in plan["plan"]:
        action = step.get("action")
        if action not in ALLOWED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")
        outputs.append({
            "step": step["step"],
            "action": action,
            "result": _execute_action(action, plan["goal"], docs)
        })
    return {
        "goal": plan["goal"],
        "outputs": outputs,
        "source_titles": [d["title"] for d in docs],
        "completed_steps": len(outputs),
        "audit": {
            "execution_mode": "local deterministic prototype",
            "external_side_effects": False,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    }

def _execute_action(action, goal, docs):
    sentences = [(d["title"], s) for d in docs for s in _sentences(d["content"])]
    if action == "summarize":
        return [{"source": t, "summary": " ".join(_sentences(next(d["content"] for d in docs if d["title"] == t))[:3])}
                for t in dict.fromkeys(d["title"] for d in docs)]
    if action == "extract":
        facts = []
        for title, sentence in sentences:
            if re.search(r"\d|20\d{2}|deadline|must|required|owner|budget|date", sentence, re.I):
                facts.append({"source": title, "fact": sentence})
        return facts[:100]
    if action == "classify":
        labels = {}
        patterns = {
            "finance": r"budget|cost|revenue|profit|price",
            "timeline": r"deadline|date|week|month|schedule|launch",
            "people": r"team|owner|customer|employee|manager",
            "technology": r"api|software|system|database|model|server"
        }
        for doc in docs:
            found = [label for label, pattern in patterns.items() if re.search(pattern, doc["content"], re.I)]
            labels[doc["title"]] = found or ["general"]
        return labels
    if action == "draft":
        evidence = [s for _, s in sentences[:8]]
        return {"draft": f"Goal: {goal}\n\nBased on the supplied materials:\n" + "\n".join(f"- {s}" for s in evidence),
                "evidence_sentences": len(evidence)}
    if action == "checklist":
        tasks = []
        for title, sentence in sentences:
            if re.search(r"\b(need to|must|should|will|complete|prepare|submit|review|create|deliver)\b", sentence, re.I):
                tasks.append({"task": sentence, "source": title, "status": "open"})
        return tasks[:100]
    raise ValueError(f"Unsupported action: {action}")
