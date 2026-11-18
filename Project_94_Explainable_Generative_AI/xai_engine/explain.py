"""Transparent feature-attribution utilities for a simple text classifier."""
from __future__ import annotations
import math
import re

DEFAULT_WEIGHTS = {
    "urgent": 1.8, "asap": 1.5, "invoice": 1.2, "payment": 1.0,
    "error": 1.4, "failed": 1.3, "timeout": 1.4, "refund": 1.1,
    "meeting": 0.7, "schedule": 0.8, "hello": 0.2, "thanks": 0.1
}

def tokenize(text):
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    return re.findall(r"[a-zA-Z0-9']+", text.lower())

def explain_text(text, weights=None, threshold=1.5):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty.")
    if not isinstance(threshold, (int, float)) or not math.isfinite(threshold):
        raise ValueError("Threshold must be a finite number.")
    weights = DEFAULT_WEIGHTS if weights is None else weights
    if not isinstance(weights, dict):
        raise ValueError("Weights must be a dictionary.")
    for token, weight in weights.items():
        if not isinstance(token, str) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("Each feature needs a string token and finite numeric weight.")
    tokens = tokenize(text)
    contributions = []
    for token in tokens:
        if token in weights:
            contributions.append({"feature": token, "weight": float(weights[token]),
                                  "evidence": f"Token '{token}' appeared in the input."})
    score = sum(x["weight"] for x in contributions)
    label = "priority" if score >= threshold else "normal"
    positive = sorted(contributions, key=lambda x: x["weight"], reverse=True)
    return {
        "prediction": label,
        "score": round(score, 4),
        "threshold": float(threshold),
        "feature_contributions": contributions,
        "top_explanations": positive[:5],
        "unmatched_tokens": [t for t in tokens if t not in weights],
        "method": "Additive keyword-weight baseline",
        "limitations": [
            "This is a transparent rule-based demonstration, not an LLM explanation.",
            "Feature contribution shows the rule that fired, not causal reasoning.",
            "The model does not understand negation, context, sarcasm or Tamil text."
        ]
    }

def compare_explanations(text, weights=None, thresholds=(1.0, 1.5, 2.5)):
    return [{"threshold": float(t), **explain_text(text, weights, t)} for t in thresholds]

def validate_explanation(result):
    required = {"prediction", "score", "threshold", "feature_contributions", "method"}
    if not isinstance(result, dict) or not required.issubset(result):
        raise ValueError("Explanation result is missing required fields.")
    if result["prediction"] not in {"priority", "normal"}:
        raise ValueError("Unknown prediction label.")
    if not isinstance(result["feature_contributions"], list):
        raise ValueError("feature_contributions must be a list.")
    return True
