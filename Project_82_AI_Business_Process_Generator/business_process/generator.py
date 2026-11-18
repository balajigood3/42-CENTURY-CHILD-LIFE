"""Rule-based business process design generator with validated structured output."""
from __future__ import annotations
import re

ROLES = {
    "sales": "Sales team", "customer": "Customer", "support": "Support team",
    "manager": "Manager", "finance": "Finance team", "hr": "HR team",
    "employee": "Employee", "it": "IT team", "system": "Business system",
    "admin": "Administrator", "operations": "Operations team"
}

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def _infer_roles(description: str):
    lower = description.lower()
    roles = []
    for key, label in ROLES.items():
        if re.search(rf"\b{re.escape(key)}\b", lower):
            roles.append(label)
    return roles or ["Process owner", "Business system"]

def generate_process(description: str, process_name: str = "Generated business process",
                     objective: str = "", include_controls: bool = True) -> dict:
    """Generate a reusable process blueprint from a plain-language description."""
    description = _clean(description)
    if len(description) < 15:
        raise ValueError("Process description must contain at least 15 characters.")
    if len(description) > 5000:
        raise ValueError("Process description must be 5000 characters or fewer.")
    process_name = _clean(process_name) or "Generated business process"
    if len(process_name) > 120:
        raise ValueError("Process name must be 120 characters or fewer.")
    objective = _clean(objective) or f"Standardize and improve: {process_name}"
    roles = _infer_roles(description)
    steps = [
        {"id": "S1", "name": "Receive request or trigger", "owner": roles[0],
         "type": "start", "description": "Capture the request, source, timestamp and required details."},
        {"id": "S2", "name": "Validate required information", "owner": "Process owner",
         "type": "task", "description": "Check completeness, format, eligibility and duplicate submissions."},
        {"id": "G1", "name": "Information complete?", "owner": "Process owner",
         "type": "gateway", "description": "If incomplete, return for correction; otherwise continue."},
        {"id": "S3", "name": "Perform business review", "owner": roles[-1],
         "type": "task", "description": "Apply the documented business rules and record the decision rationale."},
        {"id": "G2", "name": "Approval required and granted?", "owner": "Authorized approver",
         "type": "gateway", "description": "Route approval to an authorized person; reject or escalate when needed."},
        {"id": "S4", "name": "Execute approved outcome", "owner": "Business system",
         "type": "task", "description": "Update the system of record and notify relevant stakeholders."},
        {"id": "S5", "name": "Close and retain audit record", "owner": "Process owner",
         "type": "end", "description": "Record outcome, evidence, timestamps and follow-up actions."}
    ]
    risks = [
        {"risk": "Incomplete or inaccurate input", "control": "Required-field validation and correction loop", "severity": "Medium"},
        {"risk": "Unauthorized approval", "control": "Role-based approval authority and separation of duties", "severity": "High"},
        {"risk": "Untraceable process decisions", "control": "Append-only audit events and decision rationale", "severity": "High"},
        {"risk": "Processing delays", "control": "SLA monitoring, queue ownership and escalation", "severity": "Medium"}
    ] if include_controls else []
    kpis = [
        {"name": "End-to-end cycle time", "definition": "Time from request receipt to closure", "unit": "hours"},
        {"name": "First-pass completion rate", "definition": "Requests accepted without rework / total requests", "unit": "%"},
        {"name": "SLA attainment", "definition": "Requests completed within target / completed requests", "unit": "%"},
        {"name": "Exception rate", "definition": "Requests routed to exception handling / total requests", "unit": "%"}
    ]
    mermaid = """flowchart TD
    A([Receive request]) --> B[Validate information]
    B --> C{Complete?}
    C -- No --> D[Return for correction]
    D --> B
    C -- Yes --> E[Business review]
    E --> F{Approval granted?}
    F -- No --> G[Reject or escalate]
    F -- Yes --> H[Execute approved outcome]
    G --> I[Close and audit]
    H --> I
    """
    return {
        "process_name": process_name, "objective": objective,
        "source_description": description, "stakeholders": roles,
        "steps": steps, "risks_and_controls": risks, "kpis": kpis,
        "mermaid_flowchart": mermaid.strip(),
        "assumptions": [
            "The workflow is a generic starting blueprint inferred from the description.",
            "Approval thresholds, legal requirements and system integrations must be confirmed by the process owner.",
            "No business transaction or external action is executed by this generator."
        ]
    }

def validate_process(data: dict) -> dict:
    required = {"process_name", "objective", "source_description", "stakeholders",
                "steps", "risks_and_controls", "kpis", "mermaid_flowchart", "assumptions"}
    if not isinstance(data, dict) or not required.issubset(data):
        raise ValueError("Process output is missing required top-level fields.")
    if not all(isinstance(data[k], str) and data[k].strip()
               for k in ("process_name", "objective", "source_description", "mermaid_flowchart")):
        raise ValueError("Process text fields must be non-empty strings.")
    if not isinstance(data["steps"], list) or len(data["steps"]) < 3:
        raise ValueError("At least three process steps are required.")
    seen = set()
    for step in data["steps"]:
        if not isinstance(step, dict) or not all(
            isinstance(step.get(k), str) and step[k].strip()
            for k in ("id", "name", "owner", "type", "description")
        ):
            raise ValueError("Each step must have id, name, owner, type and description.")
        if step["id"] in seen:
            raise ValueError("Process step IDs must be unique.")
        seen.add(step["id"])
    for field in ("stakeholders", "risks_and_controls", "kpis", "assumptions"):
        if not isinstance(data[field], list):
            raise ValueError(f"{field} must be a list.")
    return data
