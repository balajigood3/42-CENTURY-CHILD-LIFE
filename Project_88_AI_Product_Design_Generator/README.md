# Project 88 — AI Product Design Generator

Turn a product idea into an initial product concept, personas, feature backlog, MVP scope, requirements, roadmap, metrics and risks.

## Features
- Product problem and audience input
- Heuristic domain detection
- User persona drafts
- Prioritized feature backlog
- MVP scope
- Functional and non-functional requirement starters
- Delivery roadmap
- Success metrics
- Risk and mitigation suggestions
- JSON and Markdown export
- Streamlit UI, pandas, pytest, Docker and Docker Compose
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
Product problem + audience → domain heuristic → persona / feature templates → MVP / requirement / roadmap generation → validated concept → JSON / Markdown export.

## Limitations
- This is deterministic template-based generation, not a trained generative model.
- Domain detection and feature suggestions are keyword-driven and may not fit a specific product context.
- Personas, priorities, requirements, timelines and metrics are draft suggestions, not validated research.
- Conduct user interviews, competitive analysis, feasibility review, privacy/security assessment and accessibility testing before implementation.
