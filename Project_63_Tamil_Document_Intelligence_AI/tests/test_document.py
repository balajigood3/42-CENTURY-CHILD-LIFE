import pytest
from tamil_docs.analysis import detect_language, chunk_text, keywords, search_chunks, extractive_summary
from tamil_docs.assistant import inspect_document, ask_document
from tamil_docs.extractor import extract_text, ExtractionError

def test_detect_tamil_and_mixed():
    assert detect_language("தமிழ் ஆவணம்") == "Tamil"
    assert detect_language("தமிழ் AI") == "Tamil-English mixed"

def test_chunking_with_overlap():
    chunks = chunk_text("one two three four five six", chunk_size=12, overlap=3)
    assert len(chunks) > 1
    assert all(chunks)

def test_invalid_chunk_parameters():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=3, overlap=3)

def test_keyword_and_search():
    text = "தமிழ் செயற்கை நுண்ணறிவு. செயற்கை நுண்ணறிவு பயன்பாடுகள்."
    assert "செயற்கை" in keywords(text)
    matches = search_chunks([text, "மழை மற்றும் வானிலை"], "செயற்கை நுண்ணறிவு")
    assert matches and matches[0]["chunk_id"] == 0

def test_extractive_summary():
    assert "முதல் வாக்கியம்" in extractive_summary("முதல் வாக்கியம். இரண்டாவது வாக்கியம்.")

def test_txt_document_workflow(tmp_path):
    file = tmp_path / "sample.txt"
    file.write_text("தமிழ் செயற்கை நுண்ணறிவு ஆவணம். AI பயன்பாடுகள்.", encoding="utf-8")
    doc = inspect_document(file)
    assert doc["language"] == "Tamil-English mixed"
    result = ask_document(doc, "செயற்கை நுண்ணறிவு")
    assert result["matches"]

def test_unsupported_file_rejected(tmp_path):
    file = tmp_path / "sample.exe"
    file.write_text("data")
    with pytest.raises(ExtractionError):
        extract_text(file)
