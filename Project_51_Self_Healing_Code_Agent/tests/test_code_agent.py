import pytest
from code_agent import analyze_source, apply_safe_fixes, build_report, unified_diff

def test_valid_python_has_no_syntax_error():
    report = analyze_source("def add(a, b):\n    return a + b\n")
    assert report["syntax_valid"] is True

def test_detects_syntax_error():
    report = analyze_source("def broken(:\n    pass")
    assert report["syntax_valid"] is False
    assert report["issues"][0]["code"] == "SYNTAX_ERROR"

def test_detects_none_comparison_and_bare_except():
    source = "if value == None:\n    pass\ntry:\n    work()\nexcept:\n    pass\n"
    report = analyze_source(source)
    codes = {item["code"] for item in report["issues"]}
    assert "NONE_COMPARISON" in codes
    assert "BARE_EXCEPT" in codes

def test_detects_mutable_default():
    report = analyze_source("def add_item(item, values=[]):\n    values.append(item)\n")
    assert any(x["code"] == "MUTABLE_DEFAULT" for x in report["issues"])

def test_safe_fixes_and_syntax_validation():
    source = "if value == None:\n    pass\ntry:\n    run()\nexcept:\n    pass\n"
    fixed, changes = apply_safe_fixes(source)
    assert "value is None" in fixed
    assert "except Exception:" in fixed
    assert len(changes) == 2
    compile(fixed, "<test>", "exec")

def test_does_not_modify_invalid_python():
    with pytest.raises(SyntaxError):
        apply_safe_fixes("def broken(:\n pass")

def test_log_hints():
    report = analyze_source("x = 1", "ModuleNotFoundError: No module named 'requests'")
    assert any("requests" in hint for hint in report["log_hints"])

def test_report_and_diff():
    report = analyze_source("x = None")
    assert '"syntax_valid": true' in build_report(report)
    diff = unified_diff("x == None\n", "x is None\n")
    assert "-x == None" in diff and "+x is None" in diff

def test_rejects_oversized_source():
    with pytest.raises(ValueError):
        analyze_source("x" * 200001)
