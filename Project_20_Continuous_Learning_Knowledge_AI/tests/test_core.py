import pytest
from app.core import tokenize, split_document, rank_chunks
from app.storage import KnowledgeStore

def test_tokenize_tamil():
    assert "தமிழ்" in tokenize("தமிழ் மொழி")

def test_split_document_metadata():
    chunks = split_document("alpha beta gamma " * 80, "sample.txt", 2, 100, 15)
    assert len(chunks) > 1
    assert all(c["version"] == 2 and c["source"] == "sample.txt" for c in chunks)

def test_rank_chunks_relevance():
    chunks = [
      {"id":1,"chunk_id":"a","source":"a.txt","version":1,"text":"Python machine learning pipeline"},
      {"id":2,"chunk_id":"b","source":"b.txt","version":1,"text":"Company travel reimbursement policy"}
    ]
    got = rank_chunks("Python machine learning", chunks)
    assert got[0]["id"] == 1

def test_feedback_reranks_tie():
    chunks = [
      {"id":1,"chunk_id":"a","source":"a.txt","version":1,"text":"Python data pipeline"},
      {"id":2,"chunk_id":"b","source":"b.txt","version":1,"text":"Python data pipeline"}
    ]
    feedback = {2: {"avg_rating":5,"count":2}}
    got = rank_chunks("Python data", chunks, feedback)
    assert got[0]["id"] == 2

def test_ingest_version_and_deduplicate(tmp_path):
    store = KnowledgeStore(str(tmp_path/"db.sqlite"))
    chunk = [{"chunk_id":"doc::v1::chunk_0","chunk_index":0,"text":"first version"}]
    v1,n1,changed1 = store.ingest("doc.txt","hash1",chunk)
    assert (v1,n1,changed1) == (1,1,True)
    v_same,n_same,changed_same = store.ingest("doc.txt","hash1",chunk)
    assert (v_same,n_same,changed_same) == (1,0,False)
    chunk2 = [{"chunk_id":"doc::v2::chunk_0","chunk_index":0,"text":"second version"}]
    v2,n2,changed2 = store.ingest("doc.txt","hash2",chunk2)
    assert (v2,n2,changed2) == (2,1,True)
    assert len(store.active_chunks()) == 1
    assert store.active_chunks()[0]["version"] == 2

def test_feedback_saved(tmp_path):
    store = KnowledgeStore(str(tmp_path/"db.sqlite"))
    chunk = [{"chunk_id":"doc::v1::chunk_0","chunk_index":0,"text":"evidence"}]
    store.ingest("doc.txt","hash",chunk)
    item = store.active_chunks()[0]
    store.add_feedback(item["id"],5,"relevant")
    assert store.feedback_summary()[item["id"]]["avg_rating"] == 5.0

def test_invalid_feedback_rating(tmp_path):
    store = KnowledgeStore(str(tmp_path/"db.sqlite"))
    with pytest.raises(ValueError):
        store.add_feedback(1,6)
