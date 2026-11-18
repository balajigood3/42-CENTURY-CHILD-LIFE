import ast
import io
import zipfile
import pytest
from refactor_engine.engine import analyze_source, analyze_and_refactor, make_zip

def test_detects_bare_except_and_print():
    code = "def run():\n    try:\n        print('debug')\n    except:\n        pass\n"
    found = analyze_source(code)
    rules = {x["rule"] for x in found}
    assert "bare-except" in rules
    assert "print-debug" in rules

def test_syntax_error_rejected():
    with pytest.raises(ValueError):
        analyze_source("def broken(:\n pass")

def test_source_size_limit():
    with pytest.raises(ValueError):
        analyze_source("x = 1\n" * 40000)

def test_safe_transform_preserves_parseability_and_content():
    code = "x = 1   \nprint(x)  "
    result = analyze_and_refactor(code)
    ast.parse(result["refactored"])
    assert result["refactored"] == "x = 1\nprint(x)\n"
    assert result["original"] == code

def test_zip_integrity_and_report():
    result = analyze_and_refactor("try:\n    pass\nexcept:\n    pass\n")
    archive = make_zip(result)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        assert z.testzip() is None
        assert {"original.py", "refactored.py", "REPORT.md", "report.json"} <= set(z.namelist())
