# Project 37 — Adversarial Prompt Testing AI

A local adversarial prompt test harness for LLM applications. It classifies common prompt attack patterns and optionally scans supplied model responses for suspicious disclosure/execution signals.

## Features
- Built-in prompt injection and jailbreak-oriented test suite
- Categories: instruction override, secret extraction, role confusion, untrusted content, tool abuse, data exfiltration, policy evasion, indirect injection
- Optional response triage using simple indicators
- JSON report download and Streamlit UI
- Custom JSON test suite input
- Docker and pytest support

## Architecture
`Test cases → Input validation → Pattern classifier → Optional response scanner → Risk report`

## Requirements
Python 3.11+. No paid API keys and no hosted LLM required.

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

## Usage
Start with `samples/default_tests.json`. Paste test cases into the UI as a JSON array. If you have model responses from a separate isolated evaluation, provide them as a JSON object keyed by test ID.

## Safety and limitations
- Test prompts are treated strictly as inert text; this application never sends them to a model, executes commands, or invokes tools.
- Response checks are lexical indicators, not semantic judgments. A safe answer may be flagged and a harmful answer may be missed.
- Run any live model evaluation only in a dedicated sandbox with synthetic data, no production credentials, and no external side-effect tools.
- This is a testing aid, not a complete red-team assessment or security certification.
