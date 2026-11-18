# Project 31 – Prompt Injection Defense AI

A local, rule-based screening layer that detects common prompt-injection patterns in user prompts and untrusted retrieved text. It assigns a heuristic risk score, recommends allow/review/block, and produces a redacted view.

## Features
- Detect instruction overrides and role hijacking
- Detect requests to reveal secrets or system prompts
- Detect suspicious tool and destructive-action instructions
- Detect common untrusted-boundary manipulation phrases
- Category-based heuristic risk score
- Sanitized text output and JSON report
- Explicit untrusted-content wrapper
- Streamlit UI, Docker, and pytest tests
- No API keys and no external network calls

## Architecture
`Prompt / retrieved text → Pattern scanner → Category risk scoring → Allow / Review / Block recommendation → Sanitized text + JSON report`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run injection_guard/app.py
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

## Risk scoring
- Low (0–24): allow with caution
- Medium (25–59): human review
- High (60–100): block from privileged processing

Scores are heuristic. Multiple matches in the same category count once.

## Important security limitations
- Pattern matching cannot detect every paraphrase, obfuscation, multilingual attack, encoded payload, or novel injection.
- Benign text can trigger false positives.
- Redaction is for analyst convenience; it does not make content safe or prove that an LLM will ignore it.
- Delimiting untrusted text is defense-in-depth, not a security boundary.
- Enforce least-privilege tool access, strict allowlists, sandboxing, output validation, secrets isolation, and human approval for consequential actions.
- Do not pass raw untrusted content directly into privileged agents based only on this scanner's decision.
