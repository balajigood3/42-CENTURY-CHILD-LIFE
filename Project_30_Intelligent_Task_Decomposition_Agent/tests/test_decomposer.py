import pytest
from pydantic import ValidationError
from decomposer.models import TaskBreakdown
from decomposer.engine import fallback_breakdown, decompose_task, to_mermaid

def sample():
    return {"project":"Build a small web application","objective":"Deliver a tested web application.",
            "subtasks":[
                {"id":"S01","title":"Define scope","description":"Document the intended scope and users.","priority":"High","estimated_hours":2,"depends_on":[],"deliverable":"Scope document","acceptance_criteria":"Scope is approved."},
                {"id":"S02","title":"Build application","description":"Implement the agreed application features.","priority":"High","estimated_hours":6,"depends_on":["S01"],"deliverable":"Working app","acceptance_criteria":"Core flows work."}
            ]}

def test_valid_breakdown_and_order():
    result = TaskBreakdown.model_validate(sample())
    assert [x.id for x in result.execution_order()] == ["S01","S02"]
    assert result.total_estimated_hours == 8

def test_unknown_dependency_rejected():
    data = sample()
    data["subtasks"][1]["depends_on"] = ["S99"]
    with pytest.raises(ValidationError, match="unknown dependencies"):
        TaskBreakdown.model_validate(data)

def test_dependency_cycle_rejected():
    data = sample()
    data["subtasks"][0]["depends_on"] = ["S02"]
    with pytest.raises(ValidationError, match="cycle"):
        TaskBreakdown.model_validate(data)

def test_duplicate_ids_rejected():
    data = sample()
    data["subtasks"][1]["id"] = "S01"
    with pytest.raises(ValidationError, match="unique"):
        TaskBreakdown.model_validate(data)

def test_unknown_parent_rejected():
    data = sample()
    data["subtasks"][1]["parent_id"] = "S99"
    with pytest.raises(ValidationError, match="unknown parent"):
        TaskBreakdown.model_validate(data)

def test_parent_cycle_rejected():
    data = sample()
    data["subtasks"][0]["parent_id"] = "S02"
    data["subtasks"][1]["parent_id"] = "S01"
    with pytest.raises(ValidationError, match="Parent hierarchy"):
        TaskBreakdown.model_validate(data)

def test_fallback_and_mermaid():
    result = fallback_breakdown("Create a customer support knowledge portal")
    assert len(result.subtasks) == 8
    assert "flowchart TD" in to_mermaid(result)
    assert "S01 --> S02" in to_mermaid(result)

def test_offline_mode():
    result, status = decompose_task("Develop a secure internal reporting dashboard", use_ollama=False)
    assert result.subtasks
    assert "fallback" in status.lower()

def test_short_task_rejected():
    with pytest.raises(ValueError):
        decompose_task("tiny", use_ollama=False)
