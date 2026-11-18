
import ast
import io
import json
from zipfile import ZipFile, ZIP_DEFLATED

MAX_SOURCE_BYTES = 200_000

def annotation_name(node):
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Subscript):
        return annotation_name(node.value)
    return None

def sample_value(annotation, index=0):
    values = {
        "int": [0, 1, -1], "float": [0.0, 1.5, -2.5],
        "str": ["", "sample", "  padded  "], "bool": [False, True],
        "list": [[], [1]], "dict": [{}, {"key": "value"}],
        "tuple": [(), (1, 2)]
    }
    options = values.get(annotation or "", [None])
    return options[index % len(options)]

def analyze_functions(source):
    if not isinstance(source, str):
        raise ValueError("Source must be text.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds the 200 KB limit.")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError(f"Syntax error at line {exc.lineno}: {exc.msg}") from exc
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            args = [a for a in node.args.args if a.arg not in {"self", "cls"}]
            defaults_count = len(node.args.defaults)
            required_count = len(args) - defaults_count
            params = []
            for i, arg in enumerate(args):
                params.append({
                    "name": arg.arg,
                    "annotation": annotation_name(arg.annotation),
                    "required": i < required_count
                })
            found.append({"name": node.name, "line": node.lineno,
                          "async": isinstance(node, ast.AsyncFunctionDef), "params": params,
                          "return_annotation": annotation_name(node.returns)})
    return sorted(found, key=lambda item: item["line"])

def generate_tests(source, include_edge=True):
    functions = analyze_functions(source)
    if not functions:
        raise ValueError("No public Python functions found.")
    cases = []
    imports = ", ".join(fn["name"] for fn in functions)
    lines = [
        '"""Generated pytest skeletons. Replace placeholders before use."""',
        "import pytest",
        "# TODO: replace your_module with the actual module path.",
        f"from your_module import {imports}", ""
    ]
    for fn in functions:
        params = fn["params"]
        values = [sample_value(p["annotation"], 1) for p in params]
        call = ", ".join(repr(v) for v in values)
        lines.extend([
            f"def test_{fn['name']}_basic():",
            f"    result = {fn['name']}({call})",
            "    # TODO: assert the expected business result.",
            "    assert result is not None or result is None", ""
        ])
        cases.append({"function": fn["name"], "category": "basic",
                      "description": "Run with representative values; replace placeholder assertion."})
        if include_edge:
            for i, param in enumerate(params):
                edge_values = list(values)
                edge_values[i] = sample_value(param["annotation"], 0)
                edge_call = ", ".join(repr(v) for v in edge_values)
                lines.extend([
                    f"def test_{fn['name']}_{param['name']}_boundary():",
                    f"    result = {fn['name']}({edge_call})",
                    "    # TODO: assert the expected boundary behavior.",
                    "    assert result is not None or result is None", ""
                ])
                cases.append({"function": fn["name"], "category": "boundary",
                              "description": f"Exercise parameter '{param['name']}' with a boundary-like value."})
    return {
        "functions": functions, "function_count": len(functions),
        "cases": cases, "test_code": "\\n".join(lines),
        "metadata": {"method": "AST + deterministic templates",
                     "warning": "Assertions are placeholders; expected behavior must be supplied by a developer."}
    }

def make_zip(result):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("test_generated.py", result["test_code"])
        archive.writestr("test_plan.json", json.dumps({
            "functions": result["functions"], "cases": result["cases"],
            "metadata": result["metadata"]
        }, indent=2))
        archive.writestr("README.md", """# Generated Test Package

Replace `your_module` with the actual module import path and replace placeholder assertions with expected business behavior. Add fixtures, mocks, integration tests, and property-based tests where appropriate. Run `pytest -q` in the target project.

Generated tests are starting points, not proof of correctness.
""")
    return buffer.getvalue()
