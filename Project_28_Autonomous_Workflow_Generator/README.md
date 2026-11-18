# Project 28 – Autonomous Workflow Generator

A local-first application that converts a natural-language business task into a structured workflow, validates dependencies, orders the steps, and exports JSON and Mermaid diagram source.

## Features
- Optional local Ollama generation with `qwen2.5:3b`
- Deterministic offline fallback when Ollama is unavailable or disabled
- Pydantic schema validation and unique node IDs
- Unknown dependency and cycle detection
- Topological execution order
- JSON and Mermaid downloads
- Streamlit interface
- Docker and Docker Compose setup
- Automated tests

## Architecture
`User task → Generator (Ollama or fallback) → Pydantic schema → DAG validation → topological order → UI / JSON / Mermaid exports`

## Requirements
- Python 3.11+
- No paid API keys
- Optional: Docker + Docker Compose
- Optional: Ollama for local LLM generation

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run workflow_app/main.py
```

To use Ollama, install it separately and run:
```bash
ollama pull qwen2.5:3b
ollama serve
```
The app will fall back to a deterministic template if the model service is unavailable.

## Run with Docker
```bash
docker compose up --build
```
Open http://localhost:8501. The compose setup downloads the local model on first startup; this may take time and requires sufficient disk space.

## Run tests
```bash
pytest -q
```

## Safety and limitations
- This project generates plans; it does **not** execute workflow actions, shell commands, API calls, or external side effects.
- Always review owners, dependencies, inputs, outputs, and failure handling before operational use.
- Local model output can be incomplete or incorrect; schema and graph checks validate structure, not business correctness.
- Mermaid is exported as source text; use a Mermaid-compatible viewer to render it.
