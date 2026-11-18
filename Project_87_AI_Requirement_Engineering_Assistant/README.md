# Project 87 — AI Requirement Engineering Assistant

Analyze requirement notes and create a structured requirement register, quality flags, clarification questions, acceptance-criteria starters and traceability matrix.

## Features
- Requirement statement splitting
- Functional / non-functional / clarification classification
- Actor and action keyword extraction
- Vague wording detection
- Clarification questions
- Acceptance-criteria starters
- Requirement IDs and traceability matrix
- JSON and Markdown export
- Streamlit dashboard, pandas, pytest, Docker and Docker Compose
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
Requirement notes → statement splitting → type / actor / action heuristics → quality checks → clarification prompts and traceability → report export.

## Limitations
- This is a deterministic heuristic prototype, not an LLM-based requirements analyst.
- Classification and actor/action extraction are keyword-based and may misclassify domain-specific language.
- Acceptance criteria are generic starters, not complete testable specifications.
- It does not assign business priority, estimate cost, validate legal compliance or resolve conflicting stakeholder needs.
- Product owners, business analysts, QA and engineering teams must review all outputs before baselining requirements.
