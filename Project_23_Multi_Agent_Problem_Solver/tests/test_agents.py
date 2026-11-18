import pytest
from app.agents import MultiAgentProblemSolver

def test_empty_task_rejected():
    with pytest.raises(ValueError):
        MultiAgentProblemSolver(use_llm=False).solve("  ")

def test_fallback_runs_all_four_roles():
    result = MultiAgentProblemSolver(use_llm=False).solve("Plan a community recycling drive")
    assert result["mode"] == "template_fallback"
    assert set(result["agents"]) == {"planner", "analyst", "critic", "coordinator"}
    assert result["agents"]["coordinator"]

def test_task_is_preserved():
    task = "Improve onboarding completion"
    result = MultiAgentProblemSolver(use_llm=False).solve(task)
    assert result["task"] == task
