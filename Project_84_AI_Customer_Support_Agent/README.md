# Project 84 — AI Customer Support Agent

A local-first customer support prototype that retrieves FAQ answers, classifies intent, redacts selected sensitive patterns and drafts tickets for human follow-up.

## Features
- FAQ-based answer drafting with source IDs
- Intent classification (orders, returns, payments, account, human handoff)
- Sensitive text redaction for common patterns
- Human handoff recommendation when no FAQ matches
- Support ticket draft creation
- JSONL audit history
- Editable `data/faqs.json`
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
Customer message → sensitive-pattern redaction → intent classification → FAQ retrieval → grounded response draft / human handoff → audit log.
Ticket form → local draft record.

## Limitations and security
- This is a deterministic FAQ prototype, not a trained or autonomous LLM agent.
- Keyword matching may return an imperfect FAQ. Support staff must verify responses before sending.
- Redaction uses limited patterns and cannot guarantee detection of all personal, payment or authentication data. Do not enter secrets.
- Ticket drafts are stored locally and are not submitted to a CRM or external system.
- Add authentication, access controls, encryption, retention policies, abuse protection and monitoring before production deployment.
