# Project 68 — Tamil Educational Content Generator

தமிழில் பாடக்குறிப்பு, எளிய விளக்கம், வினா-விடை, வினாடி வினா மற்றும் பயிற்சித்தாள் உருவாக்கும் local-first application.

## Features
- பாடப்பிரிவு, தலைப்பு, கற்றல் நிலை, வடிவம் தேர்வு
- கற்றல் நோக்கத்தை prompt-இல் சேர்த்தல்
- Offline sample mode
- Optional local Ollama model (`qwen2.5:3b`)
- JSONL history and Markdown download
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

## Local LLM
```bash
ollama pull qwen2.5:3b
ollama serve
```
Select **Local Ollama LLM** in the app. Default Ollama endpoint: `http://localhost:11434`. If running Streamlit in Docker and Ollama on the host, configure the host network address; container `localhost` is not the host.

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
Streamlit UI → input validation and prompt builder → sample generator / local Ollama adapter → JSONL history.

## Limitations
- Sample mode is a structured demonstration, not dynamically generated educational material.
- LLM output can contain factual errors or curriculum mismatches. Verify with textbooks and educators.
- This project does not claim alignment with any specific board syllabus.
- Ollama requires a compatible local model and sufficient system memory.
- No paid API key is needed.
