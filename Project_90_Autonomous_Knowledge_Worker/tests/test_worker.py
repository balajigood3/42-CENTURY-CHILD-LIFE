import json
import pytest
from knowledge_worker.worker import build_plan, execute_plan
from knowledge_worker.storage import save_json, load_json

DOCS = [
    {"title": "Roadmap", "content": "The launch date is 20 November 2026. The team must complete testing. The budget is 50000."},
    {"title": "Architecture", "content": "The API uses a Python service and database. The manager should review deployment."}
]

def test_build_plan_has_ordered_steps():
    plan = build_plan("Prepare status brief", DOCS, ["summarize", "extract"])
    assert [x["step"] for x in plan["plan"]] == [1, 2]

def test_requires_goal():
    with pytest.raises(ValueError):
        build_plan("", DOCS, ["summarize"])

def test_requires_documents():
    with pytest.raises(ValueError):
        build_plan("Goal", [], ["summarize"])

def test_rejects_empty_document_content():
    with pytest.raises(ValueError):
        build_plan("Goal", [{"title": "Empty", "content": " "}], ["summarize"])

def test_rejects_unknown_action():
    with pytest.raises(ValueError):
        build_plan("Goal", DOCS, ["send_email"])

def test_rejects_duplicate_actions():
    with pytest.raises(ValueError):
        build_plan("Goal", DOCS, ["extract", "extract"])

def test_execute_all_actions():
    plan = build_plan("Prepare brief", DOCS, ["summarize", "extract", "classify", "draft", "checklist"])
    result = execute_plan(plan)
    assert result["completed_steps"] == 5
    assert result["audit"]["external_side_effects"] is False

def test_extract_finds_dates_and_requirements():
    result = execute_plan(build_plan("Find facts", DOCS, ["extract"]))
    facts = result["outputs"][0]["result"]
    assert any("20 November 2026" in x["fact"] for x in facts)

def test_classify_detects_technology():
    result = execute_plan(build_plan("Classify", DOCS, ["classify"]))
    assert "technology" in result["outputs"][0]["result"]["Architecture"]

def test_checklist_finds_actions():
    result = execute_plan(build_plan("Tasks", DOCS, ["checklist"]))
    assert any("complete testing" in x["task"] for x in result["outputs"][0]["result"])

def test_json_round_trip(tmp_path):
    plan = build_plan("Goal", DOCS, ["summarize"])
    path = tmp_path / "plan.json"
    save_json(plan, path)
    assert load_json(path)["goal"] == "Goal"

def test_execute_rejects_invalid_plan():
    with pytest.raises(ValueError):
        execute_plan({})
