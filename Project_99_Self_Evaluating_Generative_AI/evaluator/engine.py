"""Rule-based evaluation harness for generated answers."""
from __future__ import annotations
import re
from collections import Counter

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def evaluate_answer(answer, expected_keywords=None, required_phrases=None,
                    forbidden_phrases=None, min_words=1, max_words=500):
    if not isinstance(answer, str):
        raise TypeError("answer must be a string")
    expected_keywords = expected_keywords or []
    required_phrases = required_phrases or []
    forbidden_phrases = forbidden_phrases or []
    normalized = normalize(answer)
    words = re.findall(r"\b[\w'-]+\b", answer)
    keyword_hits = [term for term in expected_keywords if normalize(term) in normalized]
    missing_required = [term for term in required_phrases if normalize(term) not in normalized]
    found_forbidden = [term for term in forbidden_phrases if normalize(term) in normalized]
    checks = {
        "non_empty": bool(answer.strip()),
        "min_words": len(words) >= min_words,
        "max_words": len(words) <= max_words,
        "required_phrases": not missing_required,
        "forbidden_phrases": not found_forbidden,
        "keyword_coverage": (len(keyword_hits) / len(expected_keywords)) if expected_keywords else 1.0,
    }
    passed = all(value for key, value in checks.items()
                 if key != "keyword_coverage") and checks["keyword_coverage"] >= 0.5
    score = round(100 * (
        0.15 * checks["non_empty"] +
        0.10 * checks["min_words"] +
        0.10 * checks["max_words"] +
        0.25 * checks["required_phrases"] +
        0.25 * checks["forbidden_phrases"] +
        0.15 * checks["keyword_coverage"]
    ), 1)
    return {
        "passed": bool(passed),
        "score": score,
        "word_count": len(words),
        "checks": checks,
        "keyword_hits": keyword_hits,
        "missing_required_phrases": missing_required,
        "forbidden_phrase_hits": found_forbidden,
    }

def evaluate_batch(cases):
    results = []
    for index, case in enumerate(cases):
        result = evaluate_answer(
            case.get("answer", ""),
            expected_keywords=case.get("expected_keywords", []),
            required_phrases=case.get("required_phrases", []),
            forbidden_phrases=case.get("forbidden_phrases", []),
            min_words=case.get("min_words", 1),
            max_words=case.get("max_words", 500),
        )
        result["case_id"] = case.get("id", str(index + 1))
        results.append(result)
    passed = sum(1 for item in results if item["passed"])
    scores = [item["score"] for item in results]
    return {
        "total_cases": len(results),
        "passed_cases": passed,
        "failed_cases": len(results) - passed,
        "pass_rate": round(passed / len(results), 3) if results else 0.0,
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0.0,
        "results": results,
    }

def summarize_failures(report):
    counts = Counter()
    for result in report.get("results", []):
        for check, value in result["checks"].items():
            if check == "keyword_coverage":
                if value < 0.5:
                    counts[check] += 1
            elif not value:
                counts[check] += 1
    return dict(counts)
