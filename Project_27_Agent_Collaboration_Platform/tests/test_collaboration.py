import pytest
from app.collaboration import CollaborationPlatform, ROLES

def test_empty_task_rejected():
    with pytest.raises(ValueError):
        CollaborationPlatform(use_llm=False).collaborate(" ")

def test_four_agents_run_in_order():
    result = CollaborationPlatform(use_llm=False).collaborate("Plan a team workshop")
    assert result["workflow"] == ["planner", "researcher", "reviewer", "coordinator"]
    assert len(result["messages"]) == 4

def test_report_has_final_outcome():
    result = CollaborationPlatform(use_llm=False).collaborate("Improve a help desk workflow")
    assert result["final_outcome"] == result["messages"][-1]["message"]
    assert result["mode"] == "offline_template"

def test_role_definitions_exist():
    assert set(ROLES) == {"planner", "researcher", "reviewer", "coordinator"}
