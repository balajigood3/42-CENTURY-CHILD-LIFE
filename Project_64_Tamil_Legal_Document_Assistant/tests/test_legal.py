import pytest
from legal_assistant.analyzer import analyze_document, build_report
from legal_assistant.qa import find_passages
from legal_assistant.extract import extract_text, DocumentError

SAMPLE = """The parties agree to confidentiality and indemnity.
Either party may terminate this agreement with notice.
Payment is due within thirty days. Governing law is the law of India."""

def test_detects_clause_topics():
    result = analyze_document(SAMPLE)
    keys = {x["clause"] for x in result["clause_findings"]}
    assert {"confidentiality", "indemnity", "termination", "payment", "governing_law"} <= keys

def test_empty_document_rejected():
    with pytest.raises(ValueError):
        analyze_document(" ")

def test_report_contains_disclaimer():
    report = build_report(analyze_document(SAMPLE), "contract.txt")
    assert "not legal advice" in report.lower()

def test_passage_search():
    found = find_passages(SAMPLE, "payment thirty days")
    assert found and "Payment" in found[0]["text"]

def test_no_search_terms():
    assert find_passages(SAMPLE, "") == []

def test_txt_extraction(tmp_path):
    p = tmp_path / "legal.txt"
    p.write_text(SAMPLE, encoding="utf-8")
    assert "confidentiality" in extract_text(p)

def test_unsupported_file(tmp_path):
    p = tmp_path / "x.bin"
    p.write_text("x")
    with pytest.raises(DocumentError):
        extract_text(p)
