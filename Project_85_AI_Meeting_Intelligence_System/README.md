# Project 85 — AI Meeting Intelligence System

A local-first meeting transcript analyzer that extracts summaries, decisions, owner-task patterns, risks and follow-up questions.

## Features
- Transcript and notes input
- Meeting summary extraction
- Decision marker detection
- Action items with owner, task and status
- Risks and blockers
- Key-topic extraction
- Follow-up questions
- JSON and Markdown report export
- Streamlit UI, pytest, Docker and Docker Compose
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
Transcript → sentence segmentation → heuristic action / decision / risk extraction → structured report → JSON / Markdown export.

## Limitations and privacy
- This is a deterministic heuristic prototype, not a speech recognition or trained language model.
- It does not record meetings or transcribe audio. Supply a transcript or notes.
- Owner and task extraction expects simple name-plus-action patterns and may miss or misattribute items.
- Summary uses early transcript sentences; decisions and risks depend on configured phrases.
- Review all outputs against the original meeting before sharing.
- Do not upload confidential meeting content to an unapproved environment. Add authentication, encryption and retention controls before production use.
