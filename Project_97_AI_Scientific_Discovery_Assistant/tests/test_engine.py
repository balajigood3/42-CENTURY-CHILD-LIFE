import pytest
from scientific_discovery.engine import tokenize, analyze_research, build_hypothesis_templates

DOCS = [
    {"title": "Paper A", "text": "Data augmentation improves robustness on image classification benchmarks."},
    {"title": "Paper B", "text": "Evaluation measures accuracy and corruption error across datasets."}
]

def test_tokenize_removes_common_stopwords():
    assert tokenize("The model learns from data") == ["model", "learns", "data"]

def test_analyze_returns_document_scores():
    result = analyze_research(DOCS, "data augmentation robustness")
    assert result["document_count"] == 2
    assert result["documents"][0]["title"] == "Paper A"

def test_frequent_terms_returned():
    result = analyze_research(DOCS, "data", top_k=5)
    assert result["frequent_terms"]

def test_question_terms_missing_reported():
    result = analyze_research(DOCS, "quantum biology")
    assert set(result["question_terms_not_found"]) == {"quantum", "biology"}

def test_empty_documents_rejected():
    with pytest.raises(ValueError):
        analyze_research([], "question")

def test_empty_question_rejected():
    with pytest.raises(ValueError):
        analyze_research(DOCS, " ")

def test_missing_title_rejected():
    with pytest.raises(ValueError):
        analyze_research([{"text": "some text"}], "question")

def test_empty_document_text_rejected():
    with pytest.raises(ValueError):
        analyze_research([{"title": "A", "text": " "}], "question")

def test_top_k_bounds():
    with pytest.raises(ValueError):
        analyze_research(DOCS, "data", top_k=0)

def test_hypothesis_template_generated():
    result = build_hypothesis_templates("effect of X on Y", ["X", "Y"])
    assert "null_hypothesis" in result[0]
    assert result[0]["status"].startswith("candidate")

def test_hypothesis_requires_question():
    with pytest.raises(ValueError):
        build_hypothesis_templates("", [])

def test_non_list_missing_terms_rejected():
    with pytest.raises(ValueError):
        build_hypothesis_templates("topic", "not a list")
