# Project 83 — Intelligent Contract Analyzer

A local-first contract issue-spotting prototype. It extracts likely clauses, possible parties and date strings, highlights configured risk patterns, and exports a review report.

## Features
- Upload TXT and text-based PDF contracts, or paste text
- Detect common clause categories
- Extract possible party names and date strings
- Heuristic risk flags with evidence excerpts
- Identify configured clauses not detected
- Review checklist
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
TXT/PDF input → text extraction → clause pattern matching → risk rules → structured report → JSON/Markdown export.

## Important legal and technical limitations
- This is a demo issue-spotting tool, not legal advice, a legal opinion, or a substitute for qualified counsel.
- Pattern matching is context-insensitive and can miss negation, exceptions, definitions, cross-references, unusual drafting and jurisdiction-specific rules.
- “Clause not detected” means only that configured patterns did not match; it does not prove the clause is absent.
- Metadata extraction is heuristic and may identify incorrect parties or dates.
- Scanned/image-only PDFs require OCR, which is not included.
- Do not upload confidential or privileged contracts to an unapproved environment. Review privacy and retention requirements before processing real agreements.
