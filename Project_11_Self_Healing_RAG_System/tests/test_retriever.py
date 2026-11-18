from src.retriever import LocalRetriever,split_chunks

def test_split_chunks_returns_content():
    chunks=split_chunks("one two three four five",chunk_words=3,overlap=1)
    assert chunks[0]=="one two three"
    assert len(chunks)>=2

def test_retrieval_ranks_matching_chunk():
    r=LocalRetriever()
    r.index({"a.txt":"RAG retrieves relevant documents for a question.",
             "b.txt":"Cooking recipes use flour and water."})
    hits=r.search("RAG documents",top_k=2)
    assert hits[0]["source"]=="a.txt"
    assert hits[0]["score"]>0
