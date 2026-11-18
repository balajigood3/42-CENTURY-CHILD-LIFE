
import io
import zipfile
import pytest
from testgen.engine import analyze_functions, generate_tests, make_zip

SAMPLE = "def add(a: int, b: int) -> int:\n    return a + b\n\ndef greet(name: str = 'friend'):\n    return 'Hello ' + name\n"

def test_discovers_functions_and_annotations():
    functions = analyze_functions(SAMPLE)
    assert [f["name"] for f in functions] == ["add", "greet"]
    assert functions[0]["params"][0]["annotation"] == "int"
    assert functions[1]["params"][0]["required"] is False

def test_generates_basic_and_boundary_cases():
    result = generate_tests(SAMPLE)
    assert result["function_count"] == 2
    assert "def test_add_basic" in result["test_code"]
    assert "test_add_a_boundary" in result["test_code"]
    assert len(result["cases"]) >= 4

def test_rejects_no_functions_and_syntax_errors():
    with pytest.raises(ValueError):
        generate_tests("x = 1")
    with pytest.raises(ValueError):
        analyze_functions("def broken(: pass")

def test_source_size_limit():
    with pytest.raises(ValueError):
        analyze_functions("x=1\\n" * 40000)

def test_zip_integrity():
    result = generate_tests("def square(x: int): return x*x")
    with zipfile.ZipFile(io.BytesIO(make_zip(result))) as z:
        assert z.testzip() is None
        assert {"test_generated.py", "test_plan.json", "README.md"} <= set(z.namelist())
