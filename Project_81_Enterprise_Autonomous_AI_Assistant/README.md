# Project 81 — Enterprise Autonomous AI Assistant

A local-first enterprise assistant for department-scoped knowledge retrieval, grounded answers, audit logging, and approval-gated request drafting.

## Features
- Department-filtered internal knowledge retrieval
- Employee, Manager and IT Admin role context
- Local Ollama JSON responses with citation validation
- Offline keyword retrieval mode
- Approval-gated leave, expense and IT request drafts
- JSONL audit events and request history
- Editable JSON knowledge base
- Streamlit UI, Docker, Docker Compose, pytest
- No paid API keys

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
streamlit run app.py
```
Edit `data/knowledge.json` to add internal documents. Do not put secrets or sensitive personal data in this demo knowledge base.

## Docker
```bash
docker compose up --build
```
Open `http://localhost:8501`. For AI mode, Ollama must be reachable from the container; container localhost is not the host.

## Tests
```bash
pytest -q
```

## Architecture
User question → role/department context → keyword retrieval → local Ollama → citation validation → answer + audit log.
Request form → pending approval record; no external action is executed.

## Security and production limitations
- This is a portfolio prototype, not a production enterprise identity or authorization system. The role selector is demonstrative and is not authentication.
- Enforce real SSO, server-side authorization, document-level ACLs, encryption, retention policies and audit access controls before deployment.
- Retrieved documents are untrusted data; prompt-injection resistance is not guaranteed.
- Approval requests are only saved as drafts. No leave, expense, or IT workflow is actually submitted.
- Review privacy, legal and security requirements before using real company data.
