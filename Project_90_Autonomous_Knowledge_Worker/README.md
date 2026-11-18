# Project 90 — Autonomous Knowledge Worker

A local, bounded workflow assistant that plans and executes selected knowledge tasks over user-supplied text documents.

## Capabilities
- Accept multiple TXT/Markdown documents
- Build an explicit, ordered workflow plan
- Summarize, extract facts, classify topics, draft a brief and create a checklist
- Preserve source titles in outputs
- Export plan and results as JSON
- Streamlit interface
- Docker and Docker Compose
- No paid API keys

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501`.

## Docker
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```

## Architecture
`TXT/MD Sources -> Input Validation -> Workflow Planner -> Bounded Action Executor -> JSON Report`

## Safety and limitations
- The current executor is deterministic and rule-based, not an LLM-powered autonomous agent.
- It only processes text supplied by the user.
- It does not execute shell commands, access the network, send emails, or modify external systems.
- Extraction and classification use simple patterns and may miss context or produce false positives.
- Summaries and drafts are excerpts assembled from source sentences, not verified factual conclusions.
- Review outputs before relying on them for business decisions.
