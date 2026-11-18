import pytest
from evaluator.engine import evaluate_answer, evaluate_batch, summarize_failures

def test_passes_when_all_rules_met():
    result = evaluate_answer("RAG uses retrieval and generation with relevant documents.",
        expected_keywords=["retrieval", "generation"], required_phrases=["relevant documents"],
        forbidden_phrases=["guaranteed"], min_words=5, max_words=20)
    assert result["passed"] is True
    assert result["score"] == 100.0

def test_forbidden_phrase_fails():
    result = evaluate_answer("This is guaranteed correct output.", forbidden_phrases=["guaranteed"])
    assert result["passed"] is False
    assert result["forbidden_phrase_hits"] == ["guaranteed"]

def test_missing_required_phrase_fails():
    result = evaluate_answer("A short answer.", required_phrases=["specific evidence"])
    assert result["passed"] is False

def test_minimum_word_count_fails():
    assert evaluate_answer("tiny", min_words=3)["passed"] is False

def test_maximum_word_count_fails():
    assert evaluate_answer("one two three four", max_words=2)["passed"] is False

def test_keyword_coverage_threshold():
    result = evaluate_answer("retrieval is useful", expected_keywords=["retrieval", "embedding", "vector"])
    assert result["passed"] is False
    assert result["checks"]["keyword_coverage"] < 0.5

def test_empty_answer_fails():
    assert evaluate_answer("   ")["passed"] is False

def test_non_string_rejected():
    with pytest.raises(TypeError):
        evaluate_answer(None)

def test_batch_aggregates_results():
    report = evaluate_batch([
        {"id": "ok", "answer": "hello world", "min_words": 2},
        {"id": "bad", "answer": "", "min_words": 1}
    ])
    assert report["total_cases"] == 2
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 1
    assert report["pass_rate"] == 0.5

def test_empty_batch_safe():
    report = evaluate_batch([])
    assert report["pass_rate"] == 0
    assert report["average_score"] == 0

def test_failure_summary():
    report = evaluate_batch([{"answer": "bad", "required_phrases": ["must include"]}])
    summary = summarize_failures(report)
    assert summary["required_phrases"] == 1

def test_phrase_matching_is_case_insensitive():
    result = evaluate_answer("The VECTOR DATABASE stores embeddings.",
                             required_phrases=["vector database"])
    assert result["passed"] is True
