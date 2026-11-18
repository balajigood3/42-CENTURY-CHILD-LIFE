import pytest
from pydantic import ValidationError
from goal_agent.models import GoalPlan
from goal_agent.planner import create_plan, fallback_plan, progress_summary

def sample():
    return {"goal":"Publish a portfolio website","deadline_days":30,
            "milestones":["Prepare","Build"],
            "tasks":[
                {"id":"T01","title":"Define scope","description":"Define the portfolio pages and outcomes.","milestone":"Prepare","priority":"High","estimated_days":2,"depends_on":[],"success_criteria":"Scope documented."},
                {"id":"T02","title":"Build website","description":"Implement the pages and responsive styling.","milestone":"Build","priority":"High","estimated_days":10,"depends_on":["T01"],"success_criteria":"Website works on mobile and desktop."}
            ]}

def test_valid_plan_order():
    plan = GoalPlan.model_validate(sample())
    assert [t.id for t in plan.ordered_tasks()] == ["T01","T02"]

def test_unknown_dependency():
    data = sample()
    data["tasks"][1]["depends_on"] = ["T99"]
    with pytest.raises(ValidationError, match="unknown dependencies"):
        GoalPlan.model_validate(data)

def test_cycle_detection():
    data = sample()
    data["tasks"][0]["depends_on"] = ["T02"]
    with pytest.raises(ValidationError, match="cycle"):
        GoalPlan.model_validate(data)

def test_duplicate_task_id():
    data = sample()
    data["tasks"][1]["id"] = "T01"
    with pytest.raises(ValidationError, match="unique"):
        GoalPlan.model_validate(data)

def test_progress_readiness():
    plan = GoalPlan.model_validate(sample())
    summary = progress_summary(plan, {"T01"})
    assert summary["percent"] == 50
    assert summary["ready"] == ["T02"]
    assert summary["blocked"] == []

def test_fallback_plan():
    plan = fallback_plan("Prepare for an AI engineer interview", 21)
    assert len(plan.tasks) == 7
    assert plan.tasks[0].id == "T01"

def test_offline_create_plan():
    plan, status = create_plan("Launch a small online learning portal", 45, use_ollama=False)
    assert plan.tasks
    assert "fallback" in status.lower()

def test_invalid_short_goal():
    with pytest.raises(ValueError):
        create_plan("tiny", 10, use_ollama=False)
