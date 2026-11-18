"""Role/scope policy enforcement for a bounded demo agent."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str
    scopes: tuple[str, ...]

ROLE_DEFAULTS = {
    "viewer": ("read:docs",),
    "analyst": ("read:docs", "analyze:reports"),
    "operator": ("read:docs", "analyze:reports", "write:drafts"),
    "admin": ("read:docs", "analyze:reports", "write:drafts", "manage:users"),
}
TOOL_POLICIES = {
    "search_docs": {"scope": "read:docs", "approval": False, "description": "Search the demo knowledge base"},
    "analyze_report": {"scope": "analyze:reports", "approval": False, "description": "Analyze a demo report"},
    "create_draft": {"scope": "write:drafts", "approval": True, "description": "Create a local draft (simulated)"},
    "manage_users": {"scope": "manage:users", "approval": True, "description": "View a simulated user administration action"},
}

class AuthorizationError(Exception):
    pass

def principal_from_role(user_id: str, role: str) -> Principal:
    if role not in ROLE_DEFAULTS:
        raise ValueError(f"Unknown role: {role}")
    return Principal(user_id=user_id, role=role, scopes=ROLE_DEFAULTS[role])

def authorize(principal: Principal, tool_name: str, approved: bool = False) -> dict:
    policy = TOOL_POLICIES.get(tool_name)
    if policy is None:
        raise AuthorizationError("Tool is not registered.")
    if policy["scope"] not in principal.scopes:
        raise AuthorizationError(f"Permission denied: missing scope '{policy['scope']}'.")
    if policy["approval"] and not approved:
        return {"allowed": False, "requires_approval": True, "reason": "Explicit human approval is required."}
    return {"allowed": True, "requires_approval": False, "reason": "Authorized by policy."}
