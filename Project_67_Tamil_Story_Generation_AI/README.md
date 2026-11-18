# Project 67 — Tamil Story Generation AI

கருப்பொருள், கதை வகை, வாசகர் வயது/வகை, நீளம் ஆகியவற்றின் அடிப்படையில் தமிழ்க் கதைகளை உருவாக்கும் local-first application.

## Features
- Tamil genre and audience controls
- Offline sample story mode
- Optional local Ollama generation (`qwen2.5:3b`)
- Story history stored as JSONL
- Markdown download
- Streamlit UI, Docker, pytest
- No paid API keys

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Local LLM mode
1. Install Ollama from its official distribution.
2. Run `ollama pull qwen2.5:3b`.
3. Start Ollama (`ollama serve`, if it is not already running).
4. Select **Local Ollama model** in the app.

The Ollama endpoint defaults to `http://localhost:11434`. If running the app inside Docker while Ollama runs on the host, configure networking appropriately; `localhost` inside the container refers to the container itself.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Open `http://localhost:8501`.

## Architecture
Streamlit UI → prompt builder → template generator or Ollama HTTP adapter → JSONL story history.

## Limitations
- Offline sample mode is a deterministic demonstration, not an LLM-generated creative story.
- Ollama mode requires a compatible local model and sufficient RAM.
- Model-generated Tamil may contain grammar or factual errors; review before publishing.
- Child-friendly prompting is not a substitute for adult review.
- No paid API key or hosted model is required.
