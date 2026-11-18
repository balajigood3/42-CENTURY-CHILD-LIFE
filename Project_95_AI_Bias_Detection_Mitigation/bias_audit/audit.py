"""Fairness audit utilities for labeled tabular classification data."""
from __future__ import annotations
import math
from collections import defaultdict

def _validate_rows(rows, group_key, label_key, prediction_key):
    if not isinstance(rows, list) or not rows:
        raise ValueError("Provide a non-empty list of records.")
    required = (group_key, label_key, prediction_key)
    cleaned = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or any(k not in row for k in required):
            raise ValueError(f"Record {i+1} is missing required fields.")
        if not isinstance(row[group_key], str) or not row[group_key].strip():
            raise ValueError(f"Record {i+1} has an invalid group.")
        if row[label_key] not in (0, 1) or row[prediction_key] not in (0, 1):
            raise ValueError("Labels and predictions must be binary 0 or 1.")
        cleaned.append(row)
    return cleaned

def audit_fairness(rows, group_key="group", label_key="actual", prediction_key="predicted"):
    data = _validate_rows(rows, group_key, label_key, prediction_key)
    groups = defaultdict(list)
    for row in data:
        groups[row[group_key]].append(row)
    if len(groups) < 2:
        raise ValueError("At least two groups are required for comparison.")
    metrics = {}
    for group, items in groups.items():
        tp = sum(r[label_key] == 1 and r[prediction_key] == 1 for r in items)
        fp = sum(r[label_key] == 0 and r[prediction_key] == 1 for r in items)
        tn = sum(r[label_key] == 0 and r[prediction_key] == 0 for r in items)
        fn = sum(r[label_key] == 1 and r[prediction_key] == 0 for r in items)
        n = len(items)
        positives = tp + fn
        negatives = fp + tn
        metrics[group] = {
            "count": n,
            "selection_rate": (tp + fp) / n,
            "true_positive_rate": tp / positives if positives else None,
            "false_positive_rate": fp / negatives if negatives else None,
            "accuracy": (tp + tn) / n,
            "positive_labels": positives,
            "negative_labels": negatives
        }
    def spread(key):
        vals = [m[key] for m in metrics.values() if m[key] is not None]
        return round(max(vals) - min(vals), 6) if len(vals) >= 2 else None
    selection_gap = spread("selection_rate")
    tpr_gap = spread("true_positive_rate")
    fpr_gap = spread("false_positive_rate")
    # Descriptive flags only; no legal or universal fairness threshold is asserted.
    flags = []
    if selection_gap is not None and selection_gap > 0.1:
        flags.append("Selection-rate gap exceeds 0.10; investigate context and data quality.")
    if tpr_gap is not None and tpr_gap > 0.1:
        flags.append("True-positive-rate gap exceeds 0.10; investigate equal-opportunity differences.")
    if fpr_gap is not None and fpr_gap > 0.1:
        flags.append("False-positive-rate gap exceeds 0.10; investigate error disparities.")
    return {
        "group_metrics": metrics,
        "disparity_gaps": {
            "selection_rate_gap": selection_gap,
            "true_positive_rate_gap": tpr_gap,
            "false_positive_rate_gap": fpr_gap
        },
        "flags": flags,
        "sample_count": len(data),
        "method": "Group-wise descriptive metrics on supplied binary labels and predictions",
        "caveats": [
            "Group disparities are diagnostic signals, not proof of discrimination or causation.",
            "Small samples and missing labels can make metrics unstable.",
            "Fairness definitions can conflict; legal and domain context matters.",
            "Do not infer protected attributes or deploy automatic decisions from this report."
        ]
    }

def mitigation_experiments(rows, group_key="group", label_key="actual", prediction_key="predicted"):
    """Return transparent audit suggestions, not altered predictions."""
    result = audit_fairness(rows, group_key, label_key, prediction_key)
    suggestions = [
        "Check label quality and whether outcomes reflect historical inequities.",
        "Review feature provenance and remove unjustified proxy variables.",
        "Evaluate group sample sizes and confidence intervals.",
        "Compare multiple fairness metrics with domain stakeholders.",
        "Test candidate mitigations on a held-out set before any deployment."
    ]
    return {"audit": result, "mitigation_experiments": suggestions,
            "predictions_modified": False}
