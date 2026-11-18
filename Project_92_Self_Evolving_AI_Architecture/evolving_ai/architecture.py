"""Safe, bounded architecture proposal and evaluation loop."""
from __future__ import annotations
import json
from pathlib import Path

COMPONENTS = {
    "retrieval": {"description": "Retrieve relevant context from a local knowledge store.", "cost": 2, "capability": 3},
    "validation": {"description": "Validate outputs against explicit rules and schemas.", "cost": 1, "capability": 3},
    "memory": {"description": "Persist approved facts and workflow state.", "cost": 2, "capability": 2},
    "evaluation": {"description": "Measure output quality with a repeatable test set.", "cost": 2, "capability": 3},
    "planner": {"description": "Decompose a goal into bounded, ordered steps.", "cost": 2, "capability": 3},
    "human_review": {"description": "Require human approval before consequential actions.", "cost": 1, "capability": 2},
    "monitoring": {"description": "Record latency, failures and quality signals.", "cost": 1, "capability": 2},
}

def validate_requirements(requirements):
    if not isinstance(requirements, dict):
        raise ValueError("Requirements must be an object.")
    goal = requirements.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("A non-empty goal is required.")
    needs = requirements.get("needs", [])
    allowed = set(COMPONENTS)
    if not isinstance(needs, list) or any(x not in allowed for x in needs):
        raise ValueError(f"needs must be a list of: {', '.join(sorted(allowed))}.")
    budget = requirements.get("budget", 10)
    if not isinstance(budget, int) or budget < 1:
        raise ValueError("budget must be a positive integer.")
    return {"goal": goal.strip(), "needs": list(dict.fromkeys(needs)), "budget": budget}

def propose_architecture(requirements):
    req = validate_requirements(requirements)
    selected = list(req["needs"])
    # Core components make the proposal measurable and safer.
    for core in ("validation", "evaluation"):
        if core not in selected:
            selected.append(core)
    selected.sort(key=lambda name: (COMPONENTS[name]["cost"], name))
    total_cost = sum(COMPONENTS[x]["cost"] for x in selected)
    if total_cost > req["budget"]:
        raise ValueError(f"Selected architecture cost {total_cost} exceeds budget {req['budget']}. Reduce optional components or increase budget.")
    return {
        "goal": req["goal"],
        "budget": req["budget"],
        "components": [
            {"name": name, **COMPONENTS[name]} for name in selected
        ],
        "estimated_cost": total_cost,
        "capability_score": sum(COMPONENTS[x]["capability"] for x in selected),
        "architecture_version": 1,
        "requires_human_approval_for_changes": True,
        "change_policy": "Proposals only; no source code, production configuration, or running system is modified."
    }

def evaluate_architecture(architecture, test_results):
    if not isinstance(architecture, dict) or not isinstance(architecture.get("components"), list):
        raise ValueError("Invalid architecture proposal.")
    if not isinstance(test_results, list) or not test_results:
        raise ValueError("Provide at least one test result.")
    normalized = []
    for item in test_results:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("Each test requires a name.")
        passed = item.get("passed")
        if not isinstance(passed, bool):
            raise ValueError("Each test passed field must be boolean.")
        normalized.append({"name": item["name"].strip(), "passed": passed})
    pass_rate = sum(x["passed"] for x in normalized) / len(normalized)
    if pass_rate >= 0.9:
        status, recommendation = "healthy", "Keep the current proposal; review measured bottlenecks before changes."
    elif pass_rate >= 0.6:
        status, recommendation = "needs_review", "Inspect failed tests and propose a targeted change for human approval."
    else:
        status, recommendation = "unstable", "Do not promote; diagnose failures and revise the proposal."
    return {
        "architecture_version": architecture.get("architecture_version", 1),
        "status": status,
        "pass_rate": round(pass_rate, 4),
        "passed": sum(x["passed"] for x in normalized),
        "total": len(normalized),
        "tests": normalized,
        "recommendation": recommendation,
        "next_version_created": False
    }

def propose_evolution(current_architecture, evaluation):
    if evaluation.get("status") == "healthy":
        changes = []
    elif evaluation.get("status") == "needs_review":
        names = {x["name"] for x in current_architecture["components"]}
        changes = ["monitoring"] if "monitoring" not in names else ["human_review"]
    else:
        names = {x["name"] for x in current_architecture["components"]}
        changes = [x for x in ("monitoring", "human_review", "retrieval") if x not in names]
    return {
        "based_on_version": current_architecture.get("architecture_version", 1),
        "proposed_components_to_add": changes,
        "approval_required": True,
        "automatic_application": False,
        "rationale": evaluation.get("recommendation", "Review evaluation results.")
    }

def save_json(data, path):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
