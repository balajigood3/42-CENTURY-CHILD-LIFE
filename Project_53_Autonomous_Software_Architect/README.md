# Project 53 — Autonomous Software Architect

Generate a reviewable software architecture pack from a project brief. The tool uses deterministic rules and templates; it does not call a paid LLM API.

## Features
- Architecture proposal and technology baseline
- Mermaid logical architecture diagram
- Functional and non-functional requirements
- API contract starter and architecture decision record
- Security checklist and deployment plan
- Streamlit UI, CLI, ZIP export, and tests

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI
```bash
python -m architect.cli --name "Clinic Portal" --brief "Build a clinic booking portal with login and reminders." --scale medium --sensitivity sensitive
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
This is a deterministic architecture-assistance tool, not an autonomous production architect. It infers candidate modules from keywords and cannot verify business rules, compliance, workload, costs, or threat models. Validate all recommendations with product, engineering, security, and operations stakeholders.
