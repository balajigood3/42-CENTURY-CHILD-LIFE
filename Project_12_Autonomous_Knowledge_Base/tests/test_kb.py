from src.knowledge_base import chunk_text, AutonomousKnowledgeBase

class FakeUpload:
    def __init__(self,name,text): self.name=name; self.text=text
    def getvalue(self): return self.text.encode()

def test_chunk_text():
    parts=chunk_text("one two three four five",size=3,overlap=1)
    assert parts[0]=="one two three"
    assert len(parts)>=2

def test_ingest_is_idempotent_and_updates(tmp_path):
    kb=AutonomousKnowledgeBase(db_path=tmp_path/"kb.db")
    first=kb.ingest([FakeUpload("guide.txt","RAG retrieves relevant documents.")])
    second=kb.ingest([FakeUpload("guide.txt","RAG retrieves relevant documents.")])
    assert first["total"]==second["total"]
    changed=kb.ingest([FakeUpload("guide.txt","Updated content about vector databases.")])
    assert changed["total"]>0
    assert len(kb.list_documents())==1

def test_clear_removes_documents(tmp_path):
    kb=AutonomousKnowledgeBase(db_path=tmp_path/"kb.db")
    kb.ingest([FakeUpload("a.txt","hello knowledge base")])
    kb.clear()
    assert kb.list_documents()==[]
