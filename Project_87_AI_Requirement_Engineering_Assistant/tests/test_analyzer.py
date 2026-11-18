import json
import pytest
from requirement_engineering.analyzer import (
    split_requirements, classify_requirement, analyze_requirements, validate_analysis
)
from requirement_engineering.exporter import export_json, export_markdown

NOTES = """The customer shall create an account using an email address.
The system must authenticate users before showing account information.
The dashboard should be fast and user-friendly.
The system shall export monthly reports."""

def test_split_requirements():
    assert len(split_requirements(NOTES)) == 4

def test_short_input_rejected():
    with pytest.raises(ValueError):
        split_requirements("short")

def test_oversized_input_rejected():
    with pytest.raises(ValueError):
        split_requirements("x" * 100001)

def test_functional_classification():
    assert classify_requirement("The user shall create a report.") == "Functional"

def test_nonfunctional_classification():
    assert classify_requirement("The system must provide 99 percent availability.") == "Non-functional"

def test_needs_clarification_classification():
    assert classify_requirement("The business process is documented.") == "Needs clarification"

def test_vague_terms_flagged():
    result = analyze_requirements("The dashboard should be fast and user-friendly.")
    assert result["requirements"][0]["quality_flags"]

def test_requirement_ids_are_unique():
    result = analyze_requirements(NOTES)
    ids = [x["id"] for x in result["requirements"]]
    assert len(ids) == len(set(ids))

def test_summary_counts():
    result = analyze_requirements(NOTES)
    assert result["summary"]["total"] == 4
    assert result["summary"]["functional"] >= 2

def test_validation_accepts_result():
    assert validate_analysis(analyze_requirements(NOTES))["summary"]["total"] == 4

def test_validation_rejects_duplicate_ids():
    result = analyze_requirements(NOTES)
    result["requirements"][1]["id"] = result["requirements"][0]["id"]
    with pytest.raises(ValueError):
        validate_analysis(result)

def test_json_export(tmp_path):
    path = tmp_path / "requirements.json"
    export_json(analyze_requirements(NOTES), path)
    assert json.loads(path.read_text())["summary"]["total"] == 4

def test_markdown_export(tmp_path):
    path = tmp_path / "requirements.md"
    export_markdown(analyze_requirements(NOTES), path)
    assert "Traceability matrix" in path.read_text()
