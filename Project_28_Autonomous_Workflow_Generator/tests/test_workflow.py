import pytest
from pydantic import ValidationError
from workflow_app.schema import Workflow
from workflow_app.generator import fallback_workflow, generate_workflow, to_mermaid

def valid_data():
    return {"title":"Test workflow","objective":"Complete a test task safely.",
            "nodes":[
                {"id":"a","name":"Start task","action":"Capture the incoming request."},
                {"id":"b","name":"Review task","action":"Review the request details.","depends_on":["a"]}
            ]}

def test_valid_workflow_and_order():
    wf = Workflow.model_validate(valid_data())
    assert [n.id for n in wf.topological_nodes()] == ["a","b"]

def test_unknown_dependency_rejected():
    data = valid_data()
    data["nodes"][1]["depends_on"] = ["missing"]
    with pytest.raises(ValidationError, match="unknown dependencies"):
        Workflow.model_validate(data)

def test_cycle_rejected():
    data = valid_data()
    data["nodes"][0]["depends_on"] = ["b"]
    with pytest.raises(ValidationError, match="cycle"):
        Workflow.model_validate(data)

def test_duplicate_ids_rejected():
    data = valid_data()
    data["nodes"][1]["id"] = "a"
    with pytest.raises(ValidationError, match="unique"):
        Workflow.model_validate(data)

def test_fallback_and_mermaid():
    wf = fallback_workflow("Prepare a monthly sales performance report")
    assert len(wf.nodes) == 6
    diagram = to_mermaid(wf)
    assert "flowchart TD" in diagram
    assert "capture --> plan" in diagram

def test_no_ollama_mode():
    wf, status = generate_workflow("Organize a team onboarding process", use_ollama=False)
    assert wf.nodes
    assert "fallback" in status.lower()

def test_short_task_rejected():
    with pytest.raises(ValueError):
        generate_workflow("short", use_ollama=False)
