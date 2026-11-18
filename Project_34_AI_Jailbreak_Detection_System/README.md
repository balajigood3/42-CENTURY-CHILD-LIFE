# Project 34 – AI Jailbreak Detection System

A local, rule-based prototype that screens prompts for common jailbreak patterns, assigns a heuristic severity score, and recommends a response posture.

## Features
- Policy override detection
- Unsafe persona and role-switch cues
- Refusal suppression detection
- Encoding/obfuscation instruction cues
- Fictional framing and multi-step manipulation cues
- Severity score and block/review/caution recommendations
- JSON security report export
- Streamlit UI, Docker, and pytest tests
- No API keys and no external network calls

## Architecture
`Prompt input → Pattern rules → Attack category classification → Heuristic score → Decision recommendation → JSON report`

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run jailbreak_guard/app.py
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

## Severity bands
- 0: No configured signal
- 1–29: Low
- 30–59: Medium
- 60–100: High

## Limitations
- Pattern rules can miss paraphrased, multilingual, encoded, or novel attacks.
- Benign text can match a pattern (false positive).
- A no-match result does not establish that a prompt is safe.
- This scanner does not inspect model internals or generated outputs.
- Production deployments need defense in depth: trusted system prompts, tool allowlists, least privilege, sandboxing, output validation, rate limits, monitoring, and human approval for consequential actions.
