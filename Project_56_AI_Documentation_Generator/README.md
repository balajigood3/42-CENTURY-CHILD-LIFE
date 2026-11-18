# Project 56 — AI Documentation Generator

Generate README, API reference, architecture notes, and JSON source inventory from Python code using AST parsing and deterministic templates. No paid API keys.

## Features
- Module and class docstring extraction
- Top-level synchronous and asynchronous function discovery
- Parameter and return annotation extraction
- README, API reference, architecture inventory, JSON export
- Streamlit UI, CLI, ZIP export, and tests

## Run locally
```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

## CLI
```bash
python -m docgen.cli path/to/module.py --name "My Project" --output docs.zip
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
This describes syntax-level structure only. It does not infer runtime behavior, complete call graphs, hidden dependencies, or business rules. Review the output and add project-specific setup, examples, deployment, and operational details before publishing.
