"""A tiny agent orchestrator with authorization before every tool invocation."""
from __future__ import annotations
from .policy import Principal, TOOL_POLICIES, authorize, AuthorizationError

KNOWLEDGE = [
    {"title": "Access policy", "text": "Documents are searchable only by users with read:docs."},
    {"title": "Draft workflow", "text": "Creating a draft requires write:drafts and explicit approval."},
    {"title": "Reporting", "text": "Report analysis requires analyze:reports."},
]

def _execute_demo_tool(tool_name: str, query: str) -> str:
    """Safe, local mock implementations. No filesystem, network, shell, or external side effects."""
    if tool_name == "search_docs":
        hits = [item for item in KNOWLEDGE if query.lower() in (item["title"] + " " + item["text"]).lower()]
        return "\n".join(f"{x['title']}: {x['text']}" for x in hits) or "No matching demo documents."
    if tool_name == "analyze_report":
        return f"Demo analysis completed for: {query[:160]}"
    if tool_name == "create_draft":
        return f"Draft creation simulated: {query[:160]}"
    if tool_name == "manage_users":
        return "User administration action simulated; no account was changed."
    raise AuthorizationError("Tool is not registered.")

def run_agent(principal: Principal, tool_name: str, query: str, approved: bool = False) -> dict:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("A non-empty task description is required.")
    decision = authorize(principal, tool_name, approved)
    audit = {
        "user_id": principal.user_id,
        "role": principal.role,
        "tool": tool_name,
        "decision": "allowed" if decision["allowed"] else "approval_required",
        "reason": decision["reason"],
    }
    if not decision["allowed"]:
        return {"status": "approval_required", "result": None, "audit": audit}
    output = _execute_demo_tool(tool_name, query)
    return {"status": "completed", "result": output, "audit": audit}

def available_tools(principal: Principal) -> list[dict]:
    rows = []
    for name, policy in TOOL_POLICIES.items():
        rows.append({
            "name": name,
            "description": policy["description"],
            "scope": policy["scope"],
            "has_permission": policy["scope"] in principal.scopes,
            "requires_approval": policy["approval"],
        })
    return rows
