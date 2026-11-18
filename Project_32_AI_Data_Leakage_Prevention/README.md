# Project 32 – AI Data Leakage Prevention

A local-first data leakage screening tool that detects common personal identifiers, payment-card-like values, and credential patterns, then redacts matched values before sharing.

## Features
- Email and phone pattern detection
- Aadhaar-like and PAN-like identifier detection
- Payment-card-like number detection with Luhn validation
- API key, token, password assignment, and private-key header detection
- Heuristic risk score and recommendation
- Sanitized text and JSON report export
- Streamlit UI, Docker, and pytest tests
- No external API calls or paid API keys

## Architecture
`Text input → Local pattern scanner → Sensitive data classification → Risk scoring → Redaction → Sanitized output / report`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run leak_guard/app.py
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

## Privacy and security notes
- Scanning is performed locally by the application; no text is sent to an external API.
- The UI avoids displaying original matched values in its findings table.
- Pattern detection is heuristic and can miss formats, languages, encodings, and novel secrets; false positives are possible.
- Aadhaar/PAN patterns are format-like matches only and do not verify that an identifier is real or belongs to a person.
- Card detection uses Luhn validation but does not establish that a card is active or valid.
- This is not a certified DLP or compliance product. Use approved controls, access restrictions, encryption, audit policies, secret managers, and human review in production.
