from src.context_manager import ContextManager

def test_add_text_splits_and_caps_chunks():
    manager=ContextManager(max_chars=5)
    chunks=manager.add_text([], "abcdefghijk")
    assert chunks==["abcde","fghij","k"]

def test_add_text_keeps_only_latest_40_chunks():
    manager=ContextManager(max_chars=2)
    chunks=manager.add_text([], "x")
    chunks=manager.add_text(chunks, "y")
    for _ in range(45):
        chunks=manager.add_text(chunks,"zz")
    assert len(chunks)<=40
