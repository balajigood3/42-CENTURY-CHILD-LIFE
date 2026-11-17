from core.chunking import chunk_text

def test_empty_text():
    assert chunk_text("") == []

def test_chunking_preserves_content():
    text = "word " * 500
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) > 1
    assert all(chunks)
