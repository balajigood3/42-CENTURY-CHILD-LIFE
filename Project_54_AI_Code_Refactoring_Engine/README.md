# Project 54 — AI Code Refactoring Engine

A local Python source analyzer with deterministic, AST-based code-quality findings and conservative formatting normalization. No paid API keys or external model calls.

## Features
- Python syntax validation using `ast`
- Detect bare `except`, debug `print`, long functions, many parameters, and append-loop patterns
- Safe trailing-whitespace normalization only
- Before/after source comparison
- JSON and Markdown reports
- Streamlit UI, CLI, ZIP export, and pytest suite

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI
```bash
python -m refactor_engine.cli path/to/script.py --output report.zip
```

## Docker
```bash
docker compose up --build
```
Open http://localhost:8501.

## Tests
```bash
pip install pytest
pytest -q
```

## Safety and limitations
The engine does not execute uploaded source or run arbitrary shell commands. Automatic transformation is deliberately limited to trailing-whitespace normalization. Findings are heuristics and may have false positives/negatives. AST parsing proves syntax only, not correctness. Review all changes and run the application's own tests before merging.
