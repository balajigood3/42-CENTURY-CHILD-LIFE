# Project 55 — Intelligent Test Case Generator

Generate pytest test skeletons from Python source using AST inspection and deterministic templates. No paid API keys and no source-code execution.

## Features
- Discover public synchronous and asynchronous functions
- Read parameter names and basic annotations
- Generate basic and boundary-like test scenarios
- Export pytest skeleton, JSON test plan, and README as ZIP
- Streamlit UI and CLI
- Input size and syntax validation

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI
```bash
python -m testgen.cli path/to/module.py --output test_package.zip
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

## Limitations
Generated assertions are placeholders because expected business behavior cannot reliably be inferred from syntax alone. Replace imports and assertions, add fixtures and mocks, then run tests in the target project. AST discovery is not a substitute for code review or runtime testing.
