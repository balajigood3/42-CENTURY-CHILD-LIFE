# Project 7 — Adaptive Intelligence Assistant

## நோக்கம்
பயனர் தேர்ந்தெடுக்கும் மொழி, தொனி, பதில் நீளம் ஆகியவற்றைப் பயன்படுத்தி பதில்களை மாற்றும் local-first GenAI assistant.

## Features
- Tamil / English / Tamil + English
- Professional / Friendly / Academic / Concise tone
- Short / Balanced / Detailed responses
- Optional SQLite preference storage
- Ollama + Qwen 2.5 3B; paid API key இல்லை
- Streamlit UI, pytest suite, Docker setup

## Architecture
User → Streamlit → preference prompt builder → Ollama local model → answer.
இது explicit preference adaptation மட்டுமே; model weights-ஐ train செய்யாது.

## Local setup
```bash
ollama pull qwen2.5:3b
ollama serve
```
மற்றொரு terminal-ல்:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Browser: http://localhost:8501

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5:3b
```

## Python usage
```python
from src.assistant import AdaptiveAssistant
bot=AdaptiveAssistant()
print(bot.respond("Explain vector databases", {
 "tone":"Academic","detail":"Detailed","language":"Tamil + English"
}))
```

## Privacy and limitations
- Preferences save is optional and stored locally in `data/preferences.db`.
- Prompts go to the configured Ollama endpoint (default localhost).
- LLM answers may be inaccurate; verify high-impact outputs.
- No paid API key is required. Initial model download may require internet.
