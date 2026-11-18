# Project 33 – Secure RAG Assistant

A local, extractive Retrieval-Augmented Generation (RAG) prototype with role-based document access filtering, source references, and basic prompt-injection neutralization.

## Features
- Upload TXT, MD, CSV, and text-based PDF documents
- Split documents into paragraph chunks and store in SQLite
- Assign document visibility to `admin`, `staff`, and/or `user`
- Apply access-control filtering in SQL before retrieval ranking
- Local keyword retrieval and source citations
- Abstain when no authorized matching evidence is found
- Detect and neutralize several common instruction-override phrases in retrieved content
- Export answer and citations as JSON
- Streamlit UI, Docker Compose, pytest suite
- No paid API keys or external LLM calls

## Architecture
`Document upload → Text extraction → SQLite chunks + ACL → User role → ACL-filtered retrieval → injection phrase neutralization → cited extractive answer / abstention`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run secure_rag/app.py
```
Open http://localhost:8501.

## Run with Docker
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```

## Security design notes
- ACL filtering happens before retrieval ranking, so unauthorized chunks are not returned to the retriever.
- The UI role selector is a demo convenience, not authentication. In production, derive roles from verified sessions/identity claims and enforce server-side authorization on every operation.
- The prototype uses keyword retrieval and extractive answers rather than an LLM. This avoids model hallucination but produces limited answers.
- Prompt-injection detection is a small heuristic list; it cannot detect every attack. Treat all document content as untrusted.
- SQLite is suitable for a local demo. Production requires encryption at rest, tenant isolation, audit logs, secure upload validation, backups, rate limits, and access reviews.
- Scanned/image-only PDFs need OCR, which is not included.
