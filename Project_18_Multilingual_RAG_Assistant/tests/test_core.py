from app.core import detect_language, chunk_text, MultilingualRetriever, format_sources

def test_detect_tamil():
    assert detect_language("வணக்கம் இது தமிழ்") == "Tamil"

def test_detect_hindi():
    assert detect_language("नमस्ते दुनिया") == "Hindi/Devanagari"

def test_detect_english():
    assert detect_language("Hello, how are you?") == "English or Latin-script language"

def test_chunk_overlap_and_source():
    text = "word " * 500
    chunks = chunk_text(text, "demo.txt", chunk_size=200, overlap=30)
    assert len(chunks) > 1
    assert all(c["source"] == "demo.txt" for c in chunks)
    assert all(c["text"] for c in chunks)

def test_multilingual_retriever_returns_relevant_chunk():
    chunks = [
      {"id":"a","source":"a.txt","text":"The capital city of France is Paris.","language":"English"},
      {"id":"b","source":"b.txt","text":"தமிழ்நாட்டின் தலைநகரம் சென்னை.","language":"Tamil"}
    ]
    r = MultilingualRetriever()
    r.fit(chunks)
    results = r.search("தமிழ்நாட்டின் தலைநகரம்", top_k=2)
    assert results and results[0]["id"] == "b"

def test_empty_retriever():
    r = MultilingualRetriever()
    r.fit([])
    assert r.search("hello") == []

def test_format_sources():
    rows = format_sources([{"source":"a.txt","id":"a::0","score":.75,"language":"English"}])
    assert rows[0]["source"] == "a.txt"
