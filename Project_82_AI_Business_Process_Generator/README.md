# Project 82 — AI Business Process Generator

Generate a structured business process blueprint from a plain-language workflow description.

## Features
- Process name, objective and stakeholder extraction
- Workflow steps with owners and step types
- Decision gateways and a Mermaid flowchart
- Risks, controls and operational KPIs
- JSON and Markdown report exports
- Input and output validation
- Streamlit UI, pytest, Docker and Docker Compose
- No paid API keys or external service dependency

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
Plain-language description → bounded rule-based generator → validated process JSON → workflow / risk / KPI views → JSON or Markdown export.

## Limitations
- This is a deterministic portfolio prototype, not a trained generative model. It produces a reusable generic workflow blueprint, not a guaranteed exact process map.
- Stakeholder inference is keyword-based and may miss roles or misunderstand context.
- Process owners must verify steps, approval authority, compliance obligations, SLAs and KPIs before operational use.
- No BPMN engine, ERP integration, workflow execution or business transaction is included.
