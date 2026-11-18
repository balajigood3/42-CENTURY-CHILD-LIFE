import pytest
from multimodal_rag import (
    validate_upload, chunk_text, build_index, retrieve, answer_with_context,
    MAX_UPLOAD_BYTES
)

def test_validates_text_and_image_files():
    validate_upload("notes.md", 20)
    validate_upload("scan.PNG", 20)

@pytest.mark.parametrize("name", ["audio.mp3", "archive.zip", "document"])
def test_rejects_unsupported_upload(name):
    with pytest.raises(ValueError):
        validate_upload(name, 10)

def test_rejects_empty_and_large_upload():
    with pytest.raises(ValueError):
        validate_upload("a.txt", 0)
    with pytest.raises(ValueError):
        validate_upload("a.txt", MAX_UPLOAD_BYTES + 1)

def test_chunks_text_with_overlap():
    chunks = chunk_text("abcdefghij" * 5, source="sample", chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert chunks[0]["source"] == "sample"
    assert chunks[0]["text"][-5:] == chunks[1]["text"][:5]

def test_empty_text_returns_no_chunks():
    assert chunk_text("  ") == []

def test_build_index_skips_empty_items():
    result = build_index([{"source": "x", "text": "useful data"}, {"text": " "}, None])
    assert len(result) == 1

def test_retrieval_ranks_matching_chunk():
    chunks = build_index([
        {"source": "a.txt", "text": "The database backup runs every night."},
        {"source": "b.txt", "text": "The garden needs watering."},
    ])
    hits = retrieve("database backup", chunks)
    assert hits[0]["source"] == "a.txt"

def test_retrieval_rejects_invalid_query_and_top_k():
    with pytest.raises(ValueError):
        retrieve(" ", [])
    with pytest.raises(ValueError):
        retrieve("data", [], top_k=0)

def test_answer_includes_evidence():
    hit = {"source": "guide.md", "text": "RAG retrieves relevant passages.", "score": 2}
    result = answer_with_context("What is RAG?", [hit])
    assert "RAG retrieves relevant passages" in result["answer"]
    assert result["sources"] == [hit]

def test_no_match_is_reported():
    result = answer_with_context("question", [])
    assert "do not contain" in result["answer"]
