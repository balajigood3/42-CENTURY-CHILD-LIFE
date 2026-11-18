from __future__ import annotations
import ast
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

MAX_SOURCE_BYTES = 500_000

@dataclass
class Finding:
    rule: str
    severity: str
    line: int
    message: str
    recommendation: str

class ModernizationError(ValueError):
    pass

class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.findings = []

    def add(self, node, rule, severity, message, recommendation):
        self.findings.append(Finding(rule, severity, getattr(node, "lineno", 1), message, recommendation))

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.add(node, "bare-except", "high", "Bare except catches every exception.",
                     "Catch a specific exception type; use Exception only when broad handling is intentional.")
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            self.add(node, "broad-exception", "medium", "Catching Exception may hide unrelated programming errors.",
                     "Catch the narrowest expected exception types.")
        self.generic_visit(node)

    def visit_Global(self, node):
        self.add(node, "global-state", "medium", "Function accesses module-level state.",
                 "Pass state explicitly or encapsulate it in an object.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format" and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str):
            self.add(node, "str-format", "low", "Legacy .format() string formatting detected.",
                     "Consider an f-string for simple cases; verify format specifications first.")
        self.generic_visit(node)

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mod) and isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            self.add(node, "percent-format", "low", "Percent-based string formatting detected.",
                     "Consider an f-string after checking tuple/dictionary formatting and escaped percent signs.")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "imp" or alias.name == "distutils" or alias.name.startswith("distutils."):
                self.add(node, "deprecated-import", "high", f"Deprecated import: {alias.name}.",
                         "Use a maintained alternative such as importlib or a modern build backend.")
            if alias.name == "os":
                self.add(node, "os-path-review", "low", "Review os path operations for pathlib opportunities.",
                         "Consider pathlib.Path for filesystem path composition.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "imp" or (node.module or "").startswith("distutils"):
            self.add(node, "deprecated-import", "high", f"Deprecated import module: {node.module}.",
                     "Use a maintained alternative such as importlib or a modern build backend.")
        if node.module == "typing":
            old = {"List", "Dict", "Tuple", "Set", "Optional", "Union"}
            found = sorted({a.name for a in node.names} & old)
            if found:
                self.add(node, "legacy-typing", "low", f"Legacy typing aliases imported: {', '.join(found)}.",
                         "On Python 3.10+, consider built-in generics and X | None.")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.name != "__init__" and node.returns is None:
            self.add(node, "missing-return-hint", "low", f"Function {node.name} has no return type hint.",
                     "Add a return annotation when the intended type is clear.")
        if not ast.get_docstring(node):
            self.add(node, "missing-docstring", "low", f"Function {node.name} has no docstring.",
                     "Document purpose, arguments, return value, and important exceptions.")
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

def analyze_source(source: str) -> dict[str, Any]:
    if not isinstance(source, str):
        raise ModernizationError("Source must be text.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ModernizationError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit.")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ModernizationError(f"Python syntax error at line {exc.lineno}: {exc.msg}") from exc
    visitor = Visitor()
    visitor.visit(tree)
    findings = sorted(visitor.findings, key=lambda f: (f.line, f.rule))
    counts = {level: sum(f.severity == level for f in findings) for level in ("high", "medium", "low")}
    return {"summary": {"finding_count": len(findings), "severity_counts": counts},
            "findings": [asdict(f) for f in findings]}

def conservative_modernize(source: str) -> str:
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ModernizationError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit.")
    return "\\n".join(line.rstrip(" \\t") for line in source.splitlines()) + ("\\n" if source.endswith(("\\n", "\\r")) else "")

def analyze_file(path: str | Path) -> dict[str, Any]:
    return analyze_source(Path(path).read_text(encoding="utf-8"))
