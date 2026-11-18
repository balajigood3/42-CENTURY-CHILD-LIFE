"""Requirement parsing, quality checks and traceability utilities."""
from __future__ import annotations
import re

VAGUE_TERMS = {"fast", "easy", "user-friendly", "robust", "secure", "efficient",
               "quick", "simple", "seamless", "good", "appropriate", "etc"}
ACTORS = ["user", "administrator", "admin", "customer", "manager", "system", "operator",
          "employee", "guest", "support agent"]
VERBS = ["create", "view", "update", "delete", "search", "submit", "approve", "reject",
         "export", "import", "notify", "authenticate", "upload", "download", "generate",
         "calculate", "track", "manage", "configure", "validate"]

def split_requirements(text):
    if not isinstance(text, str) or len(text.strip()) < 15:
        raise ValueError("Provide requirement notes with at least 15 characters.")
    if len(text) > 100_000:
        raise ValueError("Requirement input exceeds 100,000 characters.")
    chunks = [x.strip(" \t-*•") for x in re.split(r"\n+|(?<=[.!?])\s+", text) if x.strip(" \t-*•")]
    return [x for x in chunks if len(x) >= 8]

def classify_requirement(sentence):
    lower = sentence.lower()
    if any(x in lower for x in ("shall", "must", "should", "the system", "user can", "users can")):
        return "Functional" if any(v in lower for v in VERBS) else "Non-functional"
    if any(x in lower for x in ("response time", "availability", "encryption", "performance",
                                 "accessibility", "throughput", "uptime", "latency")):
        return "Non-functional"
    return "Needs clarification"

def analyze_requirement(sentence, index):
    lower = sentence.lower()
    actor = next((a.title() for a in ACTORS if re.search(rf"\b{re.escape(a)}\b", lower)), "Unspecified")
    action = next((v for v in VERBS if re.search(rf"\b{v}\b", lower)), "Unspecified")
    vague = sorted(term for term in VAGUE_TERMS if re.search(rf"\b{re.escape(term)}\b", lower))
    missing = []
    if actor == "Unspecified":
        missing.append("Specify the responsible actor or system component.")
    if action == "Unspecified" and classify_requirement(sentence) == "Functional":
        missing.append("Specify the expected system action.")
    if vague:
        missing.append("Replace vague terms with measurable acceptance criteria: " + ", ".join(vague))
    if not any(x in lower for x in ("when ", "if ", "after ", "before ", "upon ")):
        missing.append("Clarify trigger or preconditions where relevant.")
    if not any(x in lower for x in ("shall", "must", "should", "can ")):
        missing.append("Use a clear, testable requirement statement.")
    return {
        "id": f"REQ-{index:03d}",
        "statement": sentence,
        "type": classify_requirement(sentence),
        "actor": actor,
        "action": action,
        "priority": "Unassigned",
        "quality_flags": ["Vague wording"] if vague else [],
        "clarification_questions": missing,
        "acceptance_criteria": [
            "Given the stated actor and preconditions, when the requirement is triggered, then the specified outcome is observable."
        ]
    }

def analyze_requirements(text):
    statements = split_requirements(text)
    items = [analyze_requirement(statement, i) for i, statement in enumerate(statements, 1)]
    return {
        "requirements": items,
        "summary": {
            "total": len(items),
            "functional": sum(x["type"] == "Functional" for x in items),
            "non_functional": sum(x["type"] == "Non-functional" for x in items),
            "needs_clarification": sum(x["type"] == "Needs clarification" for x in items),
            "with_quality_flags": sum(bool(x["quality_flags"]) for x in items)
        },
        "traceability": [{"requirement_id": x["id"], "source_statement": x["statement"],
                          "test_case_id": f"TC-{i:03d}", "test_status": "Not designed"}
                         for i, x in enumerate(items, 1)],
        "disclaimer": "Automated first-pass analysis only. Product owners and engineers must confirm interpretation, priorities, and acceptance criteria."
    }

def validate_analysis(data):
    if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
        raise ValueError("Analysis must contain a requirements list.")
    ids = set()
    for item in data["requirements"]:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item[k].strip()
            for k in ("id", "statement", "type", "actor", "action", "priority")
        ):
            raise ValueError("Each requirement must contain valid identifying fields.")
        if item["id"] in ids:
            raise ValueError("Requirement IDs must be unique.")
        ids.add(item["id"])
        if not isinstance(item.get("clarification_questions"), list):
            raise ValueError("Clarification questions must be a list.")
    if not isinstance(data.get("summary"), dict) or not isinstance(data.get("traceability"), list):
        raise ValueError("Summary and traceability are required.")
    return data
