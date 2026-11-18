# Project 61 — Tamil LLM Assistant

தமிழில் கேள்விகளைப் பெற்று பதிலளிக்கும் உள்ளூர் உதவியாளர். இணைய API அல்லது paid API key கட்டாயமில்லை.

## அம்சங்கள்
- Streamlit தமிழ் UI
- Offline demo பதில்கள்
- விருப்பமான Ollama local LLM integration
- உரையாடல் history (JSONL)
- CLI மற்றும் pytest tests
- Dockerfile + Docker Compose

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Ollama mode
Install Ollama separately, then:
```bash
ollama pull qwen2.5:3b
ollama serve
```
Choose `Local Ollama` in the UI. The model runs locally; RAM/GPU needs depend on the selected model.

## CLI
```bash
python -m tamil_assistant.cli "செயற்கை நுண்ணறிவு என்றால் என்ன?"
python -m tamil_assistant.cli --ollama --model qwen2.5:3b "RAG என்றால் என்ன?"
```

## Docker
```bash
docker compose up --build
```
The Compose stack starts the UI and Ollama service. Pull a model in the Ollama service before selecting Local Ollama.

## Tests
```bash
pytest -q
```

## Architecture
Streamlit/CLI → `core.py` → offline response rules or local Ollama HTTP API; `history.py` stores local JSONL conversation history.

## Limitations and safety
- Offline mode is a small demonstration rule set, not a trained LLM.
- Local model answers may contain errors or hallucinations; verify important information.
- Conversation history is stored locally in `data/history.jsonl`.
- No cloud API, paid key, or automatic model training is used.
