import pytest
from permission_agent.policy import principal_from_role, authorize, AuthorizationError
from permission_agent.agent import run_agent, available_tools

def test_viewer_can_search_docs():
    p = principal_from_role("u1", "viewer")
    assert run_agent(p, "search_docs", "access")["status"] == "completed"

def test_viewer_cannot_analyze_reports():
    p = principal_from_role("u1", "viewer")
    with pytest.raises(AuthorizationError):
        run_agent(p, "analyze_report", "quarterly results")

def test_operator_needs_approval_for_draft():
    p = principal_from_role("u2", "operator")
    result = run_agent(p, "create_draft", "draft a plan")
    assert result["status"] == "approval_required"

def test_approved_operator_can_create_simulated_draft():
    p = principal_from_role("u2", "operator")
    result = run_agent(p, "create_draft", "draft a plan", approved=True)
    assert result["status"] == "completed"
    assert "simulated" in result["result"]

def test_admin_can_manage_users_only_with_approval():
    p = principal_from_role("root", "admin")
    assert run_agent(p, "manage_users", "list users")["status"] == "approval_required"
    assert run_agent(p, "manage_users", "list users", approved=True)["status"] == "completed"

def test_unknown_tool_denied():
    p = principal_from_role("u", "admin")
    with pytest.raises(AuthorizationError):
        authorize(p, "run_shell")

def test_unknown_role_rejected():
    with pytest.raises(ValueError):
        principal_from_role("u", "superuser")

def test_empty_task_rejected():
    p = principal_from_role("u", "viewer")
    with pytest.raises(ValueError):
        run_agent(p, "search_docs", " ")

def test_tool_list_shows_scopes():
    p = principal_from_role("u", "viewer")
    tools = {x["name"]: x for x in available_tools(p)}
    assert tools["search_docs"]["has_permission"] is True
    assert tools["manage_users"]["has_permission"] is False
