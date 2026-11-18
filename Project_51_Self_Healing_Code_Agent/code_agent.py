"""Static Python source analyzer and conservative auto-fixer.

Uploaded source is parsed with ast but is never executed.
"""
from __future__ import annotations
import ast
import json
import re
import difflib

MAX_SOURCE_CHARS = 200_000
MAX_LOG_CHARS = 50_000

def _check_size(source: str, logs: str = "") -> None:
    if not isinstance(source, str):
        raise ValueError("Source code must be text.")
    if len(source) > MAX_SOURCE_CHARS:
        raise ValueError(f"Source exceeds the {MAX_SOURCE_CHARS:,}-character limit.")
    if len(logs) > MAX_LOG_CHARS:
        raise ValueError(f"Logs exceed the {MAX_LOG_CHARS:,}-character limit.")

def analyze_source(source: str, logs: str = "") -> dict:
    _check_size(source, logs)
    issues = []
    syntax_valid = True
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        syntax_valid = False
        issues.append({
            "severity": "ERROR",
            "line": exc.lineno or 0,
            "code": "SYNTAX_ERROR",
            "message": exc.msg,
            "suggestion": "Correct the reported syntax location, then analyze again.",
        })
        tree = None

    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                if any(isinstance(op, (ast.Eq, ast.NotEq)) for op in node.ops):
                    if any(isinstance(comp, ast.Constant) and comp.value is None
                           for comp in node.comparators):
                        issues.append({
                            "severity": "WARNING",
                            "line": node.lineno,
                            "code": "NONE_COMPARISON",
                            "message": "Comparison with None uses equality instead of identity.",
                            "suggestion": "Use `is None` or `is not None`.",
                        })
            elif isinstance(node, ast.ExceptHandler) and node.type is None:
                issues.append({
                    "severity": "WARNING",
                    "line": node.lineno,
                    "code": "BARE_EXCEPT",
                    "message": "Bare except catches system-exiting exceptions too.",
                    "suggestion": "Catch a specific exception, or use `except Exception:` when appropriate.",
                })
            elif isinstance(node, ast.FunctionDef):
                defaults = node.args.defaults
                for default in defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append({
                            "severity": "WARNING",
                            "line": default.lineno,
                            "code": "MUTABLE_DEFAULT",
                            "message": f"Function `{node.name}` has a mutable default argument.",
                            "suggestion": "Use None as the default and create the mutable value inside the function.",
                        })
                        break

    log_hints = []
    log_rules = [
        (r"ModuleNotFoundError: No module named ['\"]([^'\"]+)", "Missing dependency: install package `{}`."),
        (r"NameError: name ['\"]([^'\"]+)", "Undefined name detected: check spelling/import for `{}`."),
        (r"FileNotFoundError", "A referenced file or directory could not be found; verify its path."),
        (r"PermissionError", "The process lacks permission for a file or directory operation."),
        (r"ZeroDivisionError", "A division by zero occurred; validate the denominator before dividing."),
        (r"IndexError", "A sequence index is out of range; validate collection length and index."),
        (r"KeyError: ['\"]([^'\"]+)", "Missing dictionary key: validate key `{}` or use `.get()`."),
        (r"AssertionError", "A test assertion failed; compare expected and actual values."),
    ]
    for pattern, message in log_rules:
        match = re.search(pattern, logs)
        if match:
            log_hints.append(message.format(match.group(1)) if match.groups() else message)
    return {
        "syntax_valid": syntax_valid,
        "issues": issues,
        "log_hints": log_hints,
        "issue_count": len(issues),
    }

def apply_safe_fixes(source: str) -> tuple[str, list[str]]:
    """Apply only narrowly-scoped textual fixes that preserve expression intent."""
    _check_size(source)
    # Avoid changing invalid Python; user should repair syntax first.
    ast.parse(source)
    updated = source
    changes = []

    none_pattern = re.compile(r"(?P<lhs>[A-Za-z_][A-Za-z0-9_\.]*)\s*==\s*None\b")
    updated, count = none_pattern.subn(r"\g<lhs> is None", updated)
    if count:
        changes.append(f"Changed {count} `== None` comparison(s) to `is None`.")

    not_none_pattern = re.compile(r"(?P<lhs>[A-Za-z_][A-Za-z0-9_\.]*)\s*!=\s*None\b")
    updated, count = not_none_pattern.subn(r"\g<lhs> is not None", updated)
    if count:
        changes.append(f"Changed {count} `!= None` comparison(s) to `is not None`.")

    # Bare except replacement is conservative but still flagged for manual review.
    updated, count = re.subn(r"(?m)^([ \t]*)except[ \t]*:", r"\1except Exception:", updated)
    if count:
        changes.append(f"Replaced {count} bare except clause(s) with `except Exception:`; review intended exception types.")

    # Validate the resulting source before returning it.
    ast.parse(updated)
    return updated, changes

def build_report(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)

def unified_diff(original: str, repaired: str) -> str:
    return "".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        repaired.splitlines(keepends=True),
        fromfile="original.py",
        tofile="repaired.py",
    ))
