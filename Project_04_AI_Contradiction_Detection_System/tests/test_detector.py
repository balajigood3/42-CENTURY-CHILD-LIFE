import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from core.detector import detect_contradictions
def test_requires_both_sources():
    with pytest.raises(ValueError): detect_contradictions({"name":"A","text":"hello"},{"name":"B","text":""})
def test_allowed_statuses():
    assert {"CONTRADICTION","CONSISTENT","DIFFERENT_SCOPE","UNCLEAR"}=={"CONTRADICTION","CONSISTENT","DIFFERENT_SCOPE","UNCLEAR"}
