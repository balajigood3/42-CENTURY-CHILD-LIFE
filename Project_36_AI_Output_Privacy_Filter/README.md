# Project 36 — AI Output Privacy Filter

A local privacy layer that scans AI-generated text for common sensitive-data patterns and redacts, blocks, or reports them before display or storage.

## Features
- Detects email addresses, phone-like numbers, payment-card-like digit sequences, IPv4 addresses, API tokens, Indian PAN and Aadhaar-like identifiers
- Three modes: redact, block, report-only
- Masked evidence in findings; original values are not included in the findings
- Streamlit UI and downloadable JSON report
- Automated tests and Docker deployment

## Architecture
`Generated text → Pattern detector → Policy mode (redact/block/report) → Safe output + findings`

## Requirements
Python 3.11+. No paid API key, cloud service, or external LLM is needed.

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

## Integration example
```python
from privacy_filter.detector import filter_output
result = filter_output(model_response, mode="redact")
safe_response = result["safe_output"]
if result["status"] == "blocked":
    raise RuntimeError("Output blocked by privacy policy")
```

## Limitations and safe use
- Pattern matching is not a complete DLP system; contextual identifiers and novel secret formats may be missed.
- Phone and long-number patterns can produce false positives.
- Aadhaar/PAN checks identify format patterns, not whether an identifier is valid or belongs to a person.
- Do not log raw model output or findings containing user data without an approved retention and access policy.
- Review sensitive/high-impact outputs before disclosure.
