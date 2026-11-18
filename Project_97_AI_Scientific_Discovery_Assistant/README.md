# Project 97 — AI Scientific Discovery Assistant

A local research-note triage tool that analyzes supplied text for frequent terms, overlap with a research question, missing question terms and candidate hypothesis templates.

## Features
- Upload TXT and Markdown research notes
- Research-question keyword overlap
- Document relevance ranking
- Frequent-term extraction
- Missing question-term report
- Candidate research-gap prompts
- Hypothesis and null-hypothesis templates
- JSON report export
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
`Research Notes -> Tokenization -> Keyword & Question Overlap -> Candidate Gaps -> Hypothesis Template -> JSON Report`

## Limitations
- This tool analyzes only text supplied by the user; it does not retrieve or verify papers.
- Keyword overlap is not semantic understanding and can miss synonyms, concepts and contradictions.
- A missing keyword is not proof of a genuine research gap.
- Hypothesis templates are prompts for expert review, not scientific findings.
- Validate claims against peer-reviewed literature, methods and reproducible evidence.
