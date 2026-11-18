import pytest
from xai_engine.explain import explain_text, tokenize, compare_explanations, validate_explanation

def test_tokenize_lowercase():
    assert tokenize("URGENT Invoice!") == ["urgent", "invoice"]

def test_priority_prediction_and_explanation():
    result = explain_text("urgent invoice payment")
    assert result["prediction"] == "priority"
    assert len(result["feature_contributions"]) == 3

def test_normal_prediction():
    assert explain_text("hello there")["prediction"] == "normal"

def test_empty_input_rejected():
    with pytest.raises(ValueError):
        explain_text(" ")

def test_invalid_text_type_rejected():
    with pytest.raises(ValueError):
        explain_text(None)

def test_custom_weights():
    result = explain_text("alpha beta", {"alpha": 2.0, "beta": 0.5}, 2.0)
    assert result["prediction"] == "priority"
    assert result["score"] == 2.5

def test_nonfinite_weight_rejected():
    with pytest.raises(ValueError):
        explain_text("urgent", {"urgent": float("nan")})

def test_invalid_threshold_rejected():
    with pytest.raises(ValueError):
        explain_text("urgent", threshold=float("inf"))

def test_threshold_comparison():
    results = compare_explanations("urgent invoice", thresholds=(1, 4))
    assert results[0]["prediction"] == "priority"
    assert results[1]["prediction"] == "normal"

def test_validation_accepts_valid_explanation():
    assert validate_explanation(explain_text("urgent")) is True

def test_validation_rejects_invalid_explanation():
    with pytest.raises(ValueError):
        validate_explanation({"prediction": "unknown"})

def test_unmatched_tokens_reported():
    result = explain_text("flibbertigibbet")
    assert result["unmatched_tokens"] == ["flibbertigibbet"]
