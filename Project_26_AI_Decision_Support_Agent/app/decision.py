import json
import os
import requests

class DecisionError(Exception):
    pass

def validate_inputs(problem: str, options: list[str], criteria: list[dict]) -> None:
    if not problem.strip():
        raise DecisionError("Decision problem cannot be empty.")
    if len(options) < 2:
        raise DecisionError("Provide at least two decision options.")
    if len(options) > 8:
        raise DecisionError("Maximum 8 options are supported.")
    if not criteria:
        raise DecisionError("Provide at least one evaluation criterion.")
    if len(criteria) > 10:
        raise DecisionError("Maximum 10 criteria are supported.")
    total = 0
    for criterion in criteria:
        name = str(criterion.get("name", "")).strip()
        try:
            weight = float(criterion.get("weight", 0))
        except (TypeError, ValueError):
            raise DecisionError("Criterion weights must be numeric.")
        if not name or weight <= 0 or weight > 100:
            raise DecisionError("Each criterion needs a name and a weight between 0 and 100.")
        total += weight
    if total <= 0:
        raise DecisionError("Total criterion weight must be positive.")

def weighted_score(options: list[str], criteria: list[dict], ratings: dict) -> dict:
    """Compute weighted scores from explicit user ratings (1-5)."""
    total_weight = sum(float(c["weight"]) for c in criteria)
    results = {}
    for option in options:
        score = 0.0
        breakdown = {}
        for criterion in criteria:
            name, weight = criterion["name"], float(criterion["weight"])
            try:
                rating = float(ratings[option][name])
            except (KeyError, TypeError, ValueError):
                raise DecisionError(f"Missing rating for option '{option}', criterion '{name}'.")
            if not 1 <= rating <= 5:
                raise DecisionError("Ratings must be between 1 and 5.")
            contribution = rating * weight / total_weight
            score += contribution
            breakdown[name] = {
                "rating": rating,
                "weight": weight,
                "weighted_contribution": round(contribution, 3)
            }
        results[option] = {"score": round(score, 3), "breakdown": breakdown}
    ranking = sorted(results, key=lambda option: results[option]["score"], reverse=True)
    return {"scores": results, "ranking": ranking, "method": "weighted_sum_model"}

def explain_with_ollama(problem: str, scoring: dict, context: str = "",
                        model: str | None = None, base_url: str | None = None) -> str:
    model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
    prompt = f"""You are a cautious decision-support analyst, not the decision-maker.
Decision problem: {problem}
Computed scores (these numbers are authoritative; do not change them):
{json.dumps(scoring, ensure_ascii=False, indent=2)}
Additional context from user: {context}
Explain the ranking, trade-offs, assumptions, uncertainties, and what evidence to gather next.
Do not invent facts. Clearly state that the human user makes the final decision.
"""
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=90
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if not answer:
            raise DecisionError("Ollama returned an empty explanation.")
        return answer
    except requests.RequestException as exc:
        raise DecisionError("Could not connect to local Ollama. Use offline mode or start Ollama.") from exc

def build_decision_report(problem: str, options: list[str], criteria: list[dict],
                          ratings: dict, context: str = "", use_llm: bool = True) -> dict:
    validate_inputs(problem, options, criteria)
    scoring = weighted_score(options, criteria, ratings)
    if use_llm:
        explanation = explain_with_ollama(problem, scoring, context)
    else:
        winner = scoring["ranking"][0]
        explanation = (
            f"Based only on the ratings and weights you entered, '{winner}' has the highest "
            f"weighted score ({scoring['scores'][winner]['score']}/5). Review the breakdown, "
            "confirm the ratings are evidence-based, and consider risks not represented by the criteria. "
            "This is a decision aid, not an automatic decision."
        )
    return {"problem": problem, "options": options, "criteria": criteria,
            "scoring": scoring, "explanation": explanation,
            "human_review_required": True}
