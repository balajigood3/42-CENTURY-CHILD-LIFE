# Project 92 — Self-Evolving AI Architecture

A bounded architecture proposal and evaluation prototype. It uses test outcomes to recommend possible architecture changes, but never applies them automatically.

## Features
- Define system goals and required capabilities
- Generate component-based architecture proposals
- Enforce an abstract cost budget
- Evaluate repeatable test outcomes
- Classify architecture health
- Suggest targeted evolution proposals
- Human approval required; no automatic code or deployment changes
- Export JSON review bundle
- Streamlit, pytest, Docker and Docker Compose
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
`Goal & Requirements -> Component Proposal -> Test Evaluation -> Health Assessment -> Human-Approved Evolution Proposal`

## Limitations and safety
- This is a rule-based architecture planner, not a self-modifying AI or autonomous LLM.
- Component costs and capability scores are illustrative units, not benchmark measurements.
- Evaluation quality depends on the user-supplied tests.
- Proposed changes are advisory only; they are never applied to source code or production systems.
- Production use needs version control, staging, rollback, security review, robust evaluation and human approval.
