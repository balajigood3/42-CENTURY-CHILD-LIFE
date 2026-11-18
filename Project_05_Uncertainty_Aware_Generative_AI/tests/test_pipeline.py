import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from core.pipeline import analyze_uncertainty, ALLOWED_LEVELS

def test_empty_question_rejected():
    with pytest.raises(ValueError):
        analyze_uncertainty("  ", "")

def test_input_limit_rejected(monkeypatch):
    import core.pipeline as pipeline
    monkeypatch.setattr(pipeline, "MAX_INPUT_CHARS", 5)
    with pytest.raises(ValueError):
        pipeline.analyze_uncertainty("question", "")

def test_allowed_levels():
    assert ALLOWED_LEVELS == {"LOW", "MEDIUM", "HIGH", "INSUFFICIENT_INFORMATION"}
