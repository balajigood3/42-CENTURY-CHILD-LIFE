from app.core import split_chunks, tokenize, lexical_score, retrieve, expand_query

def sample_chunks():
    return [
      {"chunk_id":"a0","source":"a.txt","category":"engineering","text":"Python is used for machine learning pipelines."},
      {"chunk_id":"b0","source":"b.txt","category":"policy","text":"Employees should protect confidential company information."},
      {"chunk_id":"c0","source":"c.txt","category":"engineering","text":"A machine learning pipeline validates input data."}
    ]

def test_split_chunks_preserves_metadata():
    chunks = split_chunks("A sentence. " * 100, "guide.txt", "docs", 150, 20)
    assert len(chunks) > 1
    assert all(c["source"] == "guide.txt" and c["category"] == "docs" for c in chunks)

def test_tokenize_unicode_tamil():
    assert "தமிழ்" in tokenize("தமிழ் மொழி")

def test_lexical_score():
    assert lexical_score({"python","machine"}, "Python for machine learning") == 1.0

def test_retrieval_category_filter():
    result = retrieve("machine learning", sample_chunks(), category="engineering")
    assert result and all(x["category"] == "engineering" for x in result)

def test_retrieval_source_filter():
    result = retrieve("confidential company", sample_chunks(), source="b.txt")
    assert result and all(x["source"] == "b.txt" for x in result)

def test_retrieval_uses_history_as_context():
    history = [{"role":"user","content":"Tell me about Python."}]
    result = retrieve("What is it used for?", sample_chunks(), history=history)
    assert result and result[0]["source"] == "a.txt"

def test_expand_query_without_history():
    assert expand_query("Explain RAG", []) == "Explain RAG"
