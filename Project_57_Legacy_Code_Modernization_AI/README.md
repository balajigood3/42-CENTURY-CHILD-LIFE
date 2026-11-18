# Project 57 — Legacy Code Modernization AI

## தமிழ் விளக்கம்
பழைய Python source code-ஐ AST மூலம் ஆய்வு செய்து modernization வாய்ப்புகள், severity, line number, விளக்கம் மற்றும் பரிந்துரைகளை வழங்கும் local tool. இது source logic-ஐ தானாக மாற்றாது; conservative copy-யில் trailing whitespace மட்டும் சீரமைக்கப்படும்.

## Features
- AST-based Python source analysis and syntax-error reporting.
- Detects bare/broad exceptions, legacy string formatting, legacy typing aliases, deprecated imports, global state, missing annotations/docstrings, and os/pathlib review opportunities.
- Streamlit UI, CLI, JSON/Markdown report, ZIP export.
- 500 KB input limit; no arbitrary source execution.
- No paid API keys.

## Architecture
`Streamlit UI / CLI → AST Analyzer → Findings JSON → Report Exporter → ZIP`

## Local setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## CLI
```bash
python -m legacy_modernizer.cli path/to/legacy.py --out modernization_bundle.zip
```

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Open http://localhost:8501.

## Input and output
Input: pasted Python code or a `.py` file via CLI. Output: findings, severity counts, conservative source copy, `report.json`, `REPORT.md`, and ZIP report bundle.

## Limitations and safety
- Static advisor only; it does not prove correctness or security.
- Heuristic findings can produce false positives and false negatives.
- Semantic refactoring is not performed automatically.
- Review every recommendation and run project tests before adopting changes.
- Untrusted source code is parsed, never executed.
