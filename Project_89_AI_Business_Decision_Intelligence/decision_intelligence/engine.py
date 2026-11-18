"""Transparent, weighted multi-criteria decision analysis."""
from __future__ import annotations
import math

def validate_options(options):
    if not isinstance(options, list) or len(options) < 2:
        raise ValueError("Provide at least two decision options.")
    names = []
    for item in options:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError("Every option must have a non-empty name.")
        if not isinstance(item.get("scores"), dict) or not item["scores"]:
            raise ValueError(f"Option {item['name']} must contain criterion scores.")
        names.append(item["name"].strip())
    if len(names) != len(set(names)):
        raise ValueError("Option names must be unique.")
    criteria = set(options[0]["scores"])
    if not criteria or any(set(x["scores"]) != criteria for x in options):
        raise ValueError("All options must use the same criteria.")
    for item in options:
        for criterion, score in item["scores"].items():
            if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 10:
                raise ValueError(f"Score for {item['name']} / {criterion} must be between 0 and 10.")
    return sorted(criteria)

def analyze_decision(options, weights, directions=None):
    criteria = validate_options(options)
    if not isinstance(weights, dict) or set(weights) != set(criteria):
        raise ValueError("Weights must be supplied for every criterion and no others.")
    if any(not isinstance(w, (int, float)) or not math.isfinite(w) or w < 0 for w in weights.values()):
        raise ValueError("Weights must be finite, non-negative numbers.")
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("At least one criterion weight must be greater than zero.")
    directions = directions or {}
    if any(directions.get(c, "benefit") not in {"benefit", "cost"} for c in criteria):
        raise ValueError("Criterion direction must be benefit or cost.")
    normalized_weights = {c: weights[c] / total_weight for c in criteria}
    ranked = []
    for option in options:
        weighted = {}
        for criterion in criteria:
            score = float(option["scores"][criterion])
            adjusted = score if directions.get(criterion, "benefit") == "benefit" else 10 - score
            weighted[criterion] = round(adjusted * normalized_weights[criterion], 4)
        ranked.append({
            "name": option["name"].strip(),
            "raw_scores": {c: float(option["scores"][c]) for c in criteria},
            "weighted_contributions": weighted,
            "total_score": round(sum(weighted.values()), 4)
        })
    ranked.sort(key=lambda x: (-x["total_score"], x["name"].lower()))
    winner = ranked[0]
    runner_up = ranked[1]
    explanation = [
        f"{c}: weight {normalized_weights[c]*100:.1f}% (direction: {directions.get(c, 'benefit')})."
        for c in criteria
    ]
    return {
        "ranking": ranked,
        "recommended_option": winner["name"],
        "score_gap_to_runner_up": round(winner["total_score"] - runner_up["total_score"], 4),
        "normalized_weights": normalized_weights,
        "criterion_directions": {c: directions.get(c, "benefit") for c in criteria},
        "weight_explanation": explanation,
        "method": "Weighted sum model with 0–10 user-entered ratings; cost criteria are reverse-scored as 10 - score.",
        "caveats": [
            "Scores and weights are subjective inputs; the ranking is not an objective truth.",
            "Check sensitivity to alternative weights and scores before making high-impact decisions.",
            "This tool does not account for hard constraints unless they are represented separately."
        ]
    }

def sensitivity_analysis(options, weights, directions=None, shifts=(-1, 1)):
    base = analyze_decision(options, weights, directions)
    results = []
    for criterion in weights:
        for delta in shifts:
            changed = dict(weights)
            changed[criterion] = max(0, changed[criterion] + delta)
            if sum(changed.values()) == 0:
                continue
            scenario = analyze_decision(options, changed, directions)
            results.append({
                "changed_criterion": criterion,
                "weight_delta": delta,
                "recommended_option": scenario["recommended_option"],
                "score_gap": scenario["score_gap_to_runner_up"]
            })
    return {"base_recommendation": base["recommended_option"], "scenarios": results}
