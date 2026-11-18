# Project 40 — AI Trust Verification System

A local trust-signal assessment tool for claims and their source metadata. It checks a small configurable reference list of domains and flags overconfident or urgency-driven wording.

## Features
- Claim wording checks: absolute claims, urgency pressure, unsupported authority phrasing
- Source metadata checks: title, publisher, URL, domain
- Local recognized-domain reference list
- Lookalike-domain-safe exact/subdomain matching
- Risk score and independent-corroboration recommendation
- JSON report download and Streamlit UI
- Docker and automated tests

## Architecture
`Claim + Source Metadata → Wording Rules + Domain Reference Check → Trust Signals → Risk Report`

## Requirements
Python 3.11+. No paid API key, hosted model, or network access required.

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

## Important limitations
- A recognized domain does not prove that a page is genuine, current, uncompromised, or supports the claim.
- This project does not fetch URLs or fact-check claims against source contents.
- The domain list is a small illustrative allowlist and should be maintained by an administrator.
- Wording heuristics can flag valid claims and miss misleading ones.
- Treat the result as triage; verify original sources and seek independent corroboration.
