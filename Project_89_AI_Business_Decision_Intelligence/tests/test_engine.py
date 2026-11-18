import json
import pytest
from decision_intelligence.engine import analyze_decision, validate_options, sensitivity_analysis
from decision_intelligence.exporter import export_json, export_markdown

OPTIONS = [
    {"name": "A", "scores": {"Cost": 8, "Quality": 7}},
    {"name": "B", "scores": {"Cost": 6, "Quality": 9}}
]
WEIGHTS = {"Cost": 1, "Quality": 2}

def test_validate_options():
    assert validate_options(OPTIONS) == ["Cost", "Quality"]

def test_requires_two_options():
    with pytest.raises(ValueError):
        validate_options(OPTIONS[:1])

def test_duplicate_option_names_rejected():
    with pytest.raises(ValueError):
        validate_options([OPTIONS[0], {"name": "A", "scores": OPTIONS[1]["scores"]}])

def test_inconsistent_criteria_rejected():
    with pytest.raises(ValueError):
        validate_options([OPTIONS[0], {"name": "B", "scores": {"Cost": 2}}])

def test_score_out_of_range_rejected():
    bad = [{"name": "A", "scores": {"Cost": 11}}, {"name": "B", "scores": {"Cost": 4}}]
    with pytest.raises(ValueError):
        validate_options(bad)

def test_weighted_ranking():
    result = analyze_decision(OPTIONS, WEIGHTS)
    assert result["recommended_option"] == "B"

def test_cost_direction_reverses_score():
    result = analyze_decision(OPTIONS, WEIGHTS, {"Cost": "cost", "Quality": "benefit"})
    assert result["ranking"][0]["name"] == "B"

def test_zero_total_weight_rejected():
    with pytest.raises(ValueError):
        analyze_decision(OPTIONS, {"Cost": 0, "Quality": 0})

def test_missing_weight_rejected():
    with pytest.raises(ValueError):
        analyze_decision(OPTIONS, {"Cost": 1})

def test_negative_weight_rejected():
    with pytest.raises(ValueError):
        analyze_decision(OPTIONS, {"Cost": -1, "Quality": 2})

def test_sensitivity_scenarios_generated():
    result = sensitivity_analysis(OPTIONS, WEIGHTS)
    assert result["scenarios"]
    assert result["base_recommendation"] == "B"

def test_json_export(tmp_path):
    result = analyze_decision(OPTIONS, WEIGHTS)
    path = tmp_path / "decision.json"
    export_json(result, path)
    assert json.loads(path.read_text())["recommended_option"] == "B"

def test_markdown_export(tmp_path):
    result = analyze_decision(OPTIONS, WEIGHTS)
    path = tmp_path / "decision.md"
    export_markdown(result, path)
    assert "Ranking" in path.read_text()
