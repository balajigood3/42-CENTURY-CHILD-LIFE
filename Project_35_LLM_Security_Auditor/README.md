# Project 35 — LLM Security Auditor

A local, deterministic security auditor for LLM application configuration files. It flags common risky patterns and creates JSON/Markdown reports. It does not call a hosted model, execute configuration, contact URLs, or run tools.

## Features
- JSON and YAML configuration input
- Detects likely embedded API keys/secrets and redacts evidence
- Flags arbitrary shell/command tools and high-impact tools without approval
- Checks document ACLs, output validation, rate limits, audit logging, URL allowlists, human approval, and prompt trust boundaries
- Streamlit interface with downloadable reports
- Included insecure and secure examples
- Pytest suite and Docker deployment

## Architecture
`Browser → Streamlit UI → safe JSON/YAML parser → deterministic rule engine → risk score + findings → JSON/Markdown report`

## Requirements
- Python 3.11+
- No paid API key and no external model required

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Run tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Open http://localhost:8501.

## Example
Upload `samples/insecure_config.json` to see findings. Try `samples/secure_config.json` to compare.

## Security boundaries and limitations
- The auditor treats configuration as data; it never evaluates code, runs commands, or follows URLs.
- Checks are heuristic and may produce false positives or miss context-dependent issues.
- A low score does not prove an application is secure.
- This is not a penetration test, certification, or compliance assessment.
- Review findings with an experienced security engineer before production deployment.
