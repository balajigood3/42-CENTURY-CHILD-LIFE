from src.analyzer import KnowledgeGapAnalyzer

def test_normalize_valid_result():
    data = {"summary": "ok", "strengths": ["scope"], "gaps": [
        {"topic": "Testing", "priority": "HIGH", "question_to_resolve": "How tested?"}
    ]}
    result = KnowledgeGapAnalyzer._normalize(data)
    assert result["summary"] == "ok"
    assert result["gaps"][0]["priority"] == "high"

def test_normalize_invalid_priority_defaults():
    result = KnowledgeGapAnalyzer._normalize({"gaps": [{"priority": "urgent"}]})
    assert result["gaps"][0]["priority"] == "medium"

def test_fallback_is_explicit_about_heuristic():
    result = KnowledgeGapAnalyzer._fallback("A basic project overview", "")
    assert "heuristic" in result["summary"].lower()
    assert isinstance(result["gaps"], list)
