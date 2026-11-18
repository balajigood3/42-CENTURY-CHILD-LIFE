import pytest
from legacy_modernizer.analyzer import analyze_source, conservative_modernize, ModernizationError

def test_detects_modernization_patterns():
    nl = chr(10)
    source = nl.join(["from typing import List", "def greet(name):", "    try:",
                      '        return "Hi {}".format(name)', "    except:", '        return "?"', ""])
    rules = {x["rule"] for x in analyze_source(source)["findings"]}
    assert {"legacy-typing", "missing-return-hint", "missing-docstring", "str-format", "bare-except"} <= rules

def test_empty_source():
    assert analyze_source("")["summary"]["finding_count"] == 0

def test_invalid_syntax():
    with pytest.raises(ModernizationError):
        analyze_source("def broken(:")

def test_size_limit():
    with pytest.raises(ModernizationError):
        analyze_source("x = 1" * 100000)

def test_conservative_copy():
    nl = chr(10)
    assert conservative_modernize("x = 1  ") == "x = 1"
