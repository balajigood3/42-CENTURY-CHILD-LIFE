import pytest
from app.debugger import validate_python, extract_code, create_diff, debug_source, DebuggerError

def test_valid_python():
    assert validate_python("x = 1\n")[0] is True

def test_invalid_python():
    valid, message = validate_python("def broken(:\n")
    assert valid is False
    assert "SyntaxError" in message

def test_extract_fenced_python():
    assert extract_code("Example:\n```python\nx = 3\n```") == "x = 3"

def test_diff_contains_change():
    diff = create_diff("x = 1\n", "x = 2\n")
    assert "-x = 1" in diff and "+x = 2" in diff

def test_offline_debug_requires_inputs():
    with pytest.raises(DebuggerError):
        debug_source("", "Traceback", use_llm=False)

def test_offline_mode_returns_safe_diagnostic():
    result = debug_source("x = 1", "ValueError: bad value", use_llm=False)
    assert result["proposed_code"] == ""
    assert result["syntax_valid"] is False
    assert "Preliminary diagnosis" in result["analysis"]
