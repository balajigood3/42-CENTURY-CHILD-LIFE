import pytest
from bias_audit.audit import audit_fairness, mitigation_experiments

ROWS = [
    {"group": "A", "actual": 1, "predicted": 1},
    {"group": "A", "actual": 0, "predicted": 0},
    {"group": "B", "actual": 1, "predicted": 0},
    {"group": "B", "actual": 0, "predicted": 1},
]

def test_group_metrics_computed():
    result = audit_fairness(ROWS)
    assert result["group_metrics"]["A"]["accuracy"] == 1.0
    assert result["group_metrics"]["B"]["accuracy"] == 0.0

def test_selection_rate_gap():
    result = audit_fairness(ROWS)
    assert result["disparity_gaps"]["selection_rate_gap"] == 0.0

def test_tpr_gap_detected():
    result = audit_fairness(ROWS)
    assert result["disparity_gaps"]["true_positive_rate_gap"] == 1.0
    assert any("True-positive-rate" in x for x in result["flags"])

def test_requires_nonempty_records():
    with pytest.raises(ValueError):
        audit_fairness([])

def test_requires_two_groups():
    with pytest.raises(ValueError):
        audit_fairness([{"group": "A", "actual": 1, "predicted": 1}])

def test_missing_column_rejected():
    with pytest.raises(ValueError):
        audit_fairness([{"group": "A", "actual": 1}, {"group": "B", "actual": 0}])

def test_nonbinary_labels_rejected():
    bad = [{"group": "A", "actual": 2, "predicted": 1},
           {"group": "B", "actual": 0, "predicted": 0}]
    with pytest.raises(ValueError):
        audit_fairness(bad)

def test_invalid_group_rejected():
    bad = [{"group": "", "actual": 1, "predicted": 1},
           {"group": "B", "actual": 0, "predicted": 0}]
    with pytest.raises(ValueError):
        audit_fairness(bad)

def test_zero_positive_denominator_is_none():
    rows = [{"group": "A", "actual": 0, "predicted": 0},
            {"group": "B", "actual": 0, "predicted": 1}]
    result = audit_fairness(rows)
    assert result["group_metrics"]["A"]["true_positive_rate"] is None

def test_mitigation_does_not_change_predictions():
    result = mitigation_experiments(ROWS)
    assert result["predictions_modified"] is False
    assert len(result["mitigation_experiments"]) >= 3

def test_sample_count():
    assert audit_fairness(ROWS)["sample_count"] == 4

def test_missing_negative_class_tnr_not_required():
    rows = [{"group": "A", "actual": 1, "predicted": 1},
            {"group": "B", "actual": 1, "predicted": 0}]
    result = audit_fairness(rows)
    assert result["disparity_gaps"]["false_positive_rate_gap"] is None
