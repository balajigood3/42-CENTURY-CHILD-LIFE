import ast
import io
import json
import re
from zipfile import ZipFile, ZIP_DEFLATED

MAX_SOURCE_BYTES = 200_000

def analyze_source(source: str) -> list[dict]:
    if not isinstance(source, str):
        raise ValueError("Source code must be text.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ValueError("Source exceeds the 200 KB analysis limit.")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError(f"Python syntax error at line {exc.lineno}: {exc.msg}") from exc

    findings = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if len(node.body) > 30:
                findings.append({"severity": "medium", "rule": "long-function",
                                 "line": node.lineno, "message": f"Function '{node.name}' has a large body; consider extracting cohesive helpers."})
            if len(node.args.args) > 6:
                findings.append({"severity": "low", "rule": "many-parameters",
                                 "line": node.lineno, "message": f"Function '{node.name}' has {len(node.args.args)} parameters; consider a configuration object."})
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name):
            if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                if len(node.body) == 1 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Call):
                    call = node.body[0].value
                    if isinstance(call.func, ast.Attribute) and call.func.attr == "append":
                        findings.append({"severity": "low", "rule": "append-loop",
                                         "line": node.lineno, "message": "A list comprehension may be clearer if the loop only appends values."})
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({"severity": "high", "rule": "bare-except",
                             "line": node.lineno, "message": "Bare except catches system-exiting exceptions; catch specific exceptions."})
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            findings.append({"severity": "info", "rule": "print-debug",
                             "line": node.lineno, "message": "Consider structured logging instead of print in application code."})
    return sorted(findings, key=lambda x: (x["line"], x["rule"]))

def _safe_transform(source: str) -> str:
    # Only whitespace normalization is applied automatically; semantics are preserved.
    lines = source.splitlines()
    normalized = [line.rstrip() for line in lines]
    result = "\n".join(normalized)
    if source.endswith("\n") or result:
        result += "\n"
    return result

def analyze_and_refactor(source: str, apply_safe: bool = True) -> dict:
    findings = analyze_source(source)
    refactored = _safe_transform(source) if apply_safe else source
    try:
        ast.parse(refactored)
    except SyntaxError as exc:
        raise ValueError("Transformed output failed syntax validation.") from exc
    report = {
        "title": "Python Code Refactoring Report",
        "summary": f"{len(findings)} static finding(s) detected.",
        "findings": findings,
        "transformations": ["Trailing whitespace normalized; no semantic rewrite performed."] if apply_safe else [],
        "limitations": [
            "Static checks are heuristic and may miss defects or report false positives.",
            "Syntax validity does not prove runtime correctness.",
            "Review suggestions and run the project's own tests before merging."
        ]
    }
    return {"original": source, "refactored": refactored, "findings": findings, "report": report}

def make_zip(result: dict) -> bytes:
    buffer = io.BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("original.py", result["original"])
        archive.writestr("refactored.py", result["refactored"])
        archive.writestr("report.json", json.dumps(result["report"], indent=2))
        markdown = "# Code Refactoring Report\n\n" + result["report"]["summary"] + "\n\n"
        for f in result["findings"]:
            markdown += f"- **{f['severity']} — {f['rule']}**, line {f['line']}: {f['message']}\n"
        markdown += "\n## Limitations\n" + "\n".join("- " + x for x in result["report"]["limitations"])
        archive.writestr("REPORT.md", markdown)
        archive.writestr("README.txt", "Review refactored.py before use. Run project tests and code review; static checks do not guarantee correctness.\n")
    return buffer.getvalue()
