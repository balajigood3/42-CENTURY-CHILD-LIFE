# Project 62 — Tamil Code-Mixed AI

தமிழ் எழுத்து, English சொற்கள், Tanglish (romanized Tamil) ஆகியவற்றை கலந்து எழுதும் input-ஐப் புரிந்துகொள்ளும் assistant.

## Features
- Common Tanglish phrase normalization
- Tamil / English / mixed-script detection
- Offline demonstration responses
- Optional local Ollama LLM mode
- Streamlit UI, CLI, local JSONL history
- Dockerfile, Docker Compose, tests

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Local LLM
Install Ollama and run:
```bash
ollama pull qwen2.5:3b
ollama serve
```
Select Local Ollama in the UI. No paid API key is required.

## CLI
```bash
python -m code_mixed.cli "RAG na enna? simple ah sollu"
python -m code_mixed.cli --ollama "AI epdi work aagum?"
```

## Docker
```bash
docker compose up --build
```
The Ollama service is included for local model use; pull the model in that service before requesting model responses.

## Tests
```bash
pytest -q
```

## Architecture
Streamlit/CLI → `assistant.py` → `normalizer.py` → offline rules or local Ollama; `history.py` stores conversation records.

## Limitations
- Phrase normalization uses a small dictionary, not a full transliteration or Tamil NLP engine.
- Offline responses are illustrative, not general-purpose intelligence.
- Ollama responses may be inaccurate; verify important information.
- History is stored locally in `data/history.jsonl`.
