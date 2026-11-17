from core.evaluator import evaluate

def test_evaluator_rejects_unparseable_output(monkeypatch):
    import core.evaluator as evaluator
    monkeypatch.setattr(evaluator, "generate", lambda prompt: "not a structured report")
    result = evaluator.evaluate("Q", "A", "")
    assert result["status"] == "FAIL"
    assert result["score"] == 0
