import pytest
from app.decision import weighted_score, build_decision_report, DecisionError

def sample():
    options = ["A", "B"]
    criteria = [{"name": "Cost", "weight": 60}, {"name": "Quality", "weight": 40}]
    ratings = {
        "A": {"Cost": 5, "Quality": 3},
        "B": {"Cost": 3, "Quality": 5}
    }
    return options, criteria, ratings

def test_weighted_score():
    options, criteria, ratings = sample()
    result = weighted_score(options, criteria, ratings)
    assert result["scores"]["A"]["score"] == 4.2
    assert result["ranking"] == ["A", "B"]

def test_missing_rating_rejected():
    options, criteria, ratings = sample()
    del ratings["A"]["Cost"]
    with pytest.raises(DecisionError):
        weighted_score(options, criteria, ratings)

def test_rating_range_enforced():
    options, criteria, ratings = sample()
    ratings["A"]["Cost"] = 6
    with pytest.raises(DecisionError):
        weighted_score(options, criteria, ratings)

def test_report_offline_mode():
    options, criteria, ratings = sample()
    result = build_decision_report("Choose an option", options, criteria, ratings, use_llm=False)
    assert result["human_review_required"] is True
    assert result["scoring"]["ranking"][0] == "A"

def test_minimum_options_required():
    with pytest.raises(DecisionError):
        build_decision_report("Choose", ["Only one"], [{"name":"Cost","weight":100}],
                              {"Only one":{"Cost":4}}, use_llm=False)
