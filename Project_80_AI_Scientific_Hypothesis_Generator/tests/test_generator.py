import pytest
from hypothesis_ai.generator import build_prompt, validate_output, offline_template, to_markdown
from hypothesis_ai.history import save_generation, load_generations

def sample():
    return {
        "field": "Ecology", "phenomenon": "Plant growth varies by light exposure.",
        "background_summary": "User notes describe possible light effects.",
        "hypotheses": [{
            "statement": "Plants receiving the defined light treatment will show a measurable difference in growth compared with controls.",
            "null_hypothesis": "There will be no measurable growth difference between groups.",
            "rationale": "The supplied background motivates testing light exposure.",
            "variables": {"independent": ["Light exposure"], "dependent": ["Growth rate"],
                          "controls": ["Water", "Soil type"]},
            "predictions": ["Mean growth rate differs between predefined groups."],
            "study_design": "Randomized controlled plant growth experiment.",
            "measurement": "Measure plant height at predefined intervals.",
            "confounders": ["Temperature variation"],
            "ethical_considerations": ["Use non-protected plant species and minimize waste."],
            "confidence": "Low"
        }],
        "validation_plan": ["Define exposure groups.", "Predefine measurement.", "Analyze outcomes."],
        "limitations": ["The literature notes may be incomplete."]
    }

def test_prompt_includes_observation():
    prompt = build_prompt("Ecology", "Plant growth varies", "Prior notes", "Experimental")
    assert "Plant growth varies" in prompt

def test_required_input_rejected():
    with pytest.raises(ValueError):
        build_prompt("Ecology", " ", "Notes", "Experimental")

def test_invalid_study_type_rejected():
    with pytest.raises(ValueError):
        build_prompt("Ecology", "Observation", "Notes", "Randomized")

def test_valid_output_passes():
    assert validate_output(sample())["field"] == "Ecology"

def test_invalid_confidence_rejected():
    data = sample()
    data["hypotheses"][0]["confidence"] = "Certain"
    with pytest.raises(ValueError):
        validate_output(data)

def test_missing_variable_list_rejected():
    data = sample()
    data["hypotheses"][0]["variables"]["dependent"] = "growth"
    with pytest.raises(ValueError):
        validate_output(data)

def test_empty_predictions_rejected():
    data = sample()
    data["hypotheses"][0]["predictions"] = []
    with pytest.raises(ValueError):
        validate_output(data)

def test_offline_template_validates_and_low_confidence():
    result = offline_template("Ecology", "Growth varies", "Notes")
    assert validate_output(result)["hypotheses"][0]["confidence"] == "Low"

def test_markdown_export():
    md = to_markdown(sample())
    assert "Null hypothesis" in md and "Validation plan" in md

def test_history_round_trip(tmp_path):
    p = tmp_path / "history.jsonl"
    save_generation(p, "Ecology", "Observation", sample())
    assert load_generations(p)[0]["result"]["field"] == "Ecology"

def test_history_limit(tmp_path):
    p = tmp_path / "history.jsonl"
    for i in range(3):
        save_generation(p, str(i), "Observation", sample())
    assert len(load_generations(p, 2)) == 2
