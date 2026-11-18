import ast
import difflib
import os
import re
import requests

class DebuggerError(Exception):
    pass

def validate_python(source: str) -> tuple[bool, str]:
    """Parse source without executing it."""
    try:
        ast.parse(source)
        return True, "Python syntax is valid."
    except SyntaxError as exc:
        return False, f"SyntaxError at line {exc.lineno}, column {exc.offset}: {exc.msg}"

def extract_code(text: str) -> str:
    """Extract a single Python fenced block if the model wraps its response."""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.I | re.S)
    return match.group(1).strip() if match else text.strip()

def create_diff(original: str, proposed: str) -> str:
    return "".join(difflib.unified_diff(
        original.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile="original.py", tofile="proposed.py"
    ))

def heuristic_suggestion(source: str, error_log: str) -> str:
    """Transparent fallback: offers diagnosis, never fabricates replacement code."""
    message = error_log.strip().splitlines()[-1] if error_log.strip() else "No error log supplied."
    return (
        "## Preliminary diagnosis\n"
        f"Last error-log line: `{message}`\n\n"
        "## Suggested debugging steps\n"
        "1. Locate the first traceback frame that points to your own source file.\n"
        "2. Inspect the referenced line and the values of its inputs.\n"
        "3. Reproduce the issue with the smallest possible input.\n"
        "4. Add a regression test for the failing case before changing the implementation.\n\n"
        "## Limitation\n"
        "The offline fallback does not infer or modify code. Connect local Ollama for an AI-proposed correction."
    )

def ask_ollama(source: str, error_log: str, model: str | None = None,
               base_url: str | None = None, timeout: int = 90) -> str:
    model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
    prompt = f"""You are a cautious Python debugging assistant.
Analyze the source and error log. Explain the likely root cause, then provide a complete corrected
Python file in one ```python fenced block. Preserve intended behavior. Do not add shell commands,
network calls, credential access, destructive operations, or unrelated features. If the evidence
is insufficient, say what is missing rather than guessing.

SOURCE CODE:
```python
{source[:18000]}
```

ERROR LOG:
```
{error_log[:8000]}
```
"""
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
        if not answer:
            raise DebuggerError("Ollama returned an empty response.")
        return answer
    except requests.RequestException as exc:
        raise DebuggerError(
            "Cannot connect to Ollama. Start Ollama and pull qwen2.5:3b, or use offline mode."
        ) from exc

def debug_source(source: str, error_log: str, use_llm: bool = True) -> dict:
    if not source.strip():
        raise DebuggerError("Source code cannot be empty.")
    if not error_log.strip():
        raise DebuggerError("Error log cannot be empty.")
    if use_llm:
        analysis = ask_ollama(source, error_log)
        proposed = extract_code(analysis)
        valid, validation = validate_python(proposed)
        diff = create_diff(source, proposed) if valid else ""
    else:
        analysis = heuristic_suggestion(source, error_log)
        proposed = ""
        valid, validation, diff = False, "No replacement code generated in offline mode.", ""
    return {
        "analysis": analysis,
        "proposed_code": proposed,
        "syntax_valid": valid,
        "validation": validation,
        "diff": diff,
        "original_syntax": validate_python(source)[1] if not validate_python(source)[0] else "Original source syntax is valid."
    }
