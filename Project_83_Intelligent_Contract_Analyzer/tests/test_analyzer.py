import json
import pytest
from contract_analyzer.analyzer import analyze_contract, extract_clauses, identify_risks
from contract_analyzer.exporter import export_json, export_markdown

SAMPLE = """Agreement between Acme Ltd and Beta Services Ltd, dated 2026-05-10.
The parties agree to payment within 30 days of invoice.
The parties shall maintain confidentiality and protect personal data.
Either party may terminate this agreement with 30 days notice.
This agreement is governed by the laws of Example State.
Any dispute shall be resolved by arbitration.
The supplier shall indemnify the customer for third-party claims.
"""

def test_analyze_extracts_key_clauses():
    result = analyze_contract(SAMPLE)
    types = {x["clause_type"] for x in result["clauses"]}
    assert {"payment", "confidentiality", "termination", "governing_law",
            "dispute_resolution", "data_protection", "indemnity"} <= types

def test_metadata_date_detected():
    result = analyze_contract(SAMPLE)
    assert "2026-05-10" in result["metadata"]["date_strings"]

def test_metadata_parties_detected():
    result = analyze_contract(SAMPLE)
    assert len(result["metadata"]["possible_parties"]) >= 2

def test_risk_flags_detect_indemnity():
    risks = identify_risks(SAMPLE)
    assert any(r["category"] == "indemnity" for r in risks)

def test_empty_text_rejected():
    with pytest.raises(ValueError):
        analyze_contract("  ")

def test_short_text_rejected():
    with pytest.raises(ValueError):
        analyze_contract("This is short.")

def test_oversized_text_rejected():
    with pytest.raises(ValueError):
        analyze_contract("x" * 200001)

def test_missing_clauses_reported():
    result = analyze_contract("A simple agreement that contains only a basic scope of work.")
    assert "governing_law" in result["clauses_not_detected"]

def test_clause_extraction_empty():
    assert extract_clauses("Plain text without legal clauses.") == []

def test_json_export(tmp_path):
    target = tmp_path / "report.json"
    export_json(analyze_contract(SAMPLE), target)
    assert json.loads(target.read_text())["filename"] == "pasted_contract.txt"

def test_markdown_export(tmp_path):
    target = tmp_path / "report.md"
    export_markdown(analyze_contract(SAMPLE), target)
    assert "Review checklist" in target.read_text()
