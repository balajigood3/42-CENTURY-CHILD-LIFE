# Project 29 – AI Goal Achievement Agent

A local-first goal planner that turns a user-defined goal and deadline into milestones, dependent tasks, success criteria, and a manually updated progress tracker.

## Features
- Natural-language goal input and deadline
- Optional local Ollama model (`qwen2.5:3b`)
- Deterministic offline fallback
- Pydantic schema validation
- Unique task IDs, dependency validation, and cycle detection
- Topological task ordering
- Manual completion tracking and progress percentage
- Ready and blocked task identification
- Export plan and progress as JSON
- Streamlit UI, Dockerfile, Docker Compose, pytest suite

## Architecture
`Goal + deadline → Planner (Ollama or fallback) → Pydantic validation → Dependency graph → Milestones / task order → Progress tracker → JSON export`

## Requirements
- Python 3.11+
- No paid API keys
- Optional: Ollama
- Optional: Docker and Docker Compose

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run goal_agent/app.py
```

Optional local LLM:
```bash
ollama pull qwen2.5:3b
ollama serve
```
If Ollama is unavailable, the planner automatically uses its deterministic fallback.

## Run with Docker
```bash
docker compose up --build
```
Open http://localhost:8501. First startup downloads the local model and may take time and disk space.

## Tests
```bash
pytest -q
```

## Limitations and safety
- The agent creates a plan and records manually checked progress; it does not execute tasks, send messages, or interact with external services.
- Estimates are planning aids, not guarantees. Reassess deadlines and dependencies as conditions change.
- Structural validation cannot prove that a plan is realistic or complete.
- Review the generated plan before relying on it for important deadlines.
