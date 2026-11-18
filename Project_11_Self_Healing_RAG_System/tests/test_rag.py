from src.rag import SelfHealingRAG

def test_no_matching_context_returns_insufficient():
    rag=SelfHealingRAG(threshold=0.9)
    result=rag.ask("quantum physics",{"notes.txt":"This file describes a simple gardening schedule."})
    assert result["status"]=="INSUFFICIENT_CONTEXT"
