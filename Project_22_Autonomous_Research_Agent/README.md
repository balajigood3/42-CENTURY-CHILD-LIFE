# Project 22 — Autonomous Research Agent

## நோக்கம்
ஒரு research topic-ஐ வைத்து web sources கண்டறிதல் அல்லது பயனர் கொடுத்த URLs-ஐ வாசித்தல், ஆதாரங்களைச் சேகரித்தல், local LLM மூலம் structured research brief உருவாக்குதல்.

## Architecture
`Topic / URLs → Source Discovery → Page Extraction → Evidence Bundle → Ollama Synthesis → Report + Source Manifest`

## Features
- DuckDuckGo public search integration; paid search API key தேவையில்லை
- User-provided URLs ஆதரவு
- HTML text extraction மற்றும் source manifest
- Ollama + Qwen 2.5 3B local synthesis
- Evidence gaps, agreement/disagreement, further research questions
- Streamlit UI, pytest tests
- Dockerfile + Docker Compose + Ollama service

## Local setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
streamlit run app/ui.py
```
Open `http://localhost:8501`.

## Docker setup
```bash
docker compose up --build -d
docker compose exec ollama ollama pull qwen2.5:3b
```
Open `http://localhost:8501`.

## Tests
```bash
pytest -q
```

## No paid API keys
Search uses the DuckDuckGo public search interface and synthesis runs on local Ollama. Internet access is required for web research; no paid LLM or search API key is configured.

## Safety and limitations
- Search provider availability and rate limits may change.
- Only http/https URLs are accepted; localhost and credential-bearing URLs are blocked.
- This is an educational research assistant, not a substitute for expert or peer-reviewed review.
- Extracted pages may contain prompt injection or misleading content. The prompt treats source text as untrusted, but model safeguards are not guaranteed.
- The generated report can still contain errors. Verify important claims against the linked original sources.
- URL validation is basic and does not fully protect against all DNS rebinding or server-side request forgery scenarios; do not expose this demo to untrusted users without hardened network egress controls.
