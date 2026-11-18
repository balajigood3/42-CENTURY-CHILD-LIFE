from src.reasoner import MultiDocumentReasoner,chunks

def test_chunks_overlap():
    result=chunks("one two three four five",size=3,overlap=1)
    assert result[0]=="one two three"
    assert result[1].startswith("three")

def test_retrieval_returns_document_level_evidence():
    engine=MultiDocumentReasoner(top_k=1)
    docs={"a.txt":"RAG retrieves documents and grounds language model answers.",
          "b.txt":"Neural networks learn patterns from training examples."}
    evidence,coverage=engine.retrieve("RAG retrieves documents",docs)
    assert evidence["a.txt"]
    assert coverage["b.txt"]["total_chunks"]>=1

def test_no_matching_terms_empty_evidence():
    engine=MultiDocumentReasoner()
    evidence,coverage=engine.retrieve("volcano",{"a.txt":"apples oranges bananas"})
    assert evidence["a.txt"]==[]
