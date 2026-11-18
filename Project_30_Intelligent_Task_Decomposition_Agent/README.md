# Project 30 – Intelligent Task Decomposition Agent

A local-first planning application that turns a complex project description into actionable subtasks with priorities, effort estimates, dependencies, deliverables, and acceptance criteria.

## Features
- Optional local Ollama model (`qwen2.5:3b`)
- Deterministic offline fallback
- Pydantic schema validation
- Task hierarchy and dependency graph validation
- Duplicate ID, unknown reference, and cycle detection
- Topological execution order
- Estimated total effort
- Mermaid dependency diagram and JSON export
- Streamlit UI, Docker Compose, pytest tests

## Architecture
`Complex task → Ollama / fallback → structured subtask JSON → hierarchy + DAG validation → execution order → UI / JSON / Mermaid`

## Requirements
- Python 3.11+
- No paid API keys
- Optional Ollama
- Optional Docker + Docker Compose

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run decomposer/app.py
```

Optional local LLM:
```bash
ollama pull qwen2.5:3b
ollama serve
```
If Ollama is unavailable, deterministic fallback planning is used.

## Run with Docker
```bash
docker compose up --build
```
Open http://localhost:8501. First startup pulls the local model and may require significant disk space and time.

## Tests
```bash
pytest -q
```

## Limitations and safety
- This is a decomposition and planning tool, not an execution agent.
- Generated subtasks and estimates require human review.
- Structural validation checks references and cycles; it cannot prove that the breakdown is complete, feasible, or correctly scoped.
- No generated shell commands or external actions are executed.
