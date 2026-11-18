# Project 39 — Untrusted Document Detection AI

A local scanner that identifies suspicious instruction-like text and potential prompt-injection content in documents before they are added to a RAG knowledge base.

## Features
- Detects instruction overrides and system-prompt extraction attempts
- Flags tool execution, data exfiltration, credential requests, authority spoofing, and URLs
- Risk score, severity, evidence snippets, and recommended action
- Upload or paste plain-text documents
- JSON report download
- File type and 2 MB size limits
- Docker deployment and pytest suite

## Architecture
`Document → Text Scanner → Rule Matcher → Risk Scoring → Quarantine/Review Recommendation`

## Requirements
Python 3.11+. No paid API keys or external model calls.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## RAG integration pattern
Run the scanner before indexing a document. If `recommended_action` is `quarantine_and_review`, keep it out of the retrieval index until a human approves it. Also enforce source ACLs separately.

## Limitations and security notes
- This is heuristic pattern matching, not malware scanning or semantic security verification.
- Benign text can trigger false positives; obfuscated or novel attacks may be missed.
- URL detection only reports URLs; it never opens or fetches them.
- The scanner does not execute scripts, macros, embedded commands, or document instructions.
- A clean result does not prove the document is trustworthy.
