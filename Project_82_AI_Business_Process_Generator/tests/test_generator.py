import json
import pytest
from business_process.generator import generate_process, validate_process
from business_process.exporter import export_json, export_markdown

DESC = "Customer submits a request and sales validates details before manager approval."

def test_generate_contains_workflow():
    result = generate_process(DESC, "Customer onboarding")
    assert len(result["steps"]) >= 3
    assert result["process_name"] == "Customer onboarding"

def test_roles_are_inferred():
    result = generate_process("HR employee sends a leave request to manager.")
    assert "HR team" in result["stakeholders"]
    assert "Manager" in result["stakeholders"]

def test_short_description_rejected():
    with pytest.raises(ValueError):
        generate_process("too short")

def test_long_description_rejected():
    with pytest.raises(ValueError):
        generate_process("x" * 5001)

def test_process_name_length_rejected():
    with pytest.raises(ValueError):
        generate_process(DESC, "x" * 121)

def test_controls_can_be_omitted():
    result = generate_process(DESC, include_controls=False)
    assert result["risks_and_controls"] == []

def test_unique_step_ids():
    result = generate_process(DESC)
    ids = [s["id"] for s in result["steps"]]
    assert len(ids) == len(set(ids))

def test_validation_rejects_missing_field():
    with pytest.raises(ValueError):
        validate_process({"process_name": "missing"})

def test_validation_rejects_duplicate_ids():
    result = generate_process(DESC)
    result["steps"][1]["id"] = result["steps"][0]["id"]
    with pytest.raises(ValueError):
        validate_process(result)

def test_validation_accepts_generated_result():
    assert validate_process(generate_process(DESC))["process_name"]

def test_json_export(tmp_path):
    result = generate_process(DESC)
    target = tmp_path / "process.json"
    export_json(result, target)
    assert json.loads(target.read_text())["steps"]

def test_markdown_export(tmp_path):
    result = generate_process(DESC)
    target = tmp_path / "process.md"
    export_markdown(result, target)
    assert "Mermaid flowchart" in target.read_text()
