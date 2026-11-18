# Project 9 — Context Loss Prevention AI

## நோக்கம்
உரையாடல் நீளமானபோது முக்கிய முடிவுகள், தேவைகள், தேதிகள், கட்டுப்பாடுகள் போன்றவற்றை compact memory-ஆகச் சுருக்கி, அடுத்த கேள்விகளுக்குப் பயன்படுத்தும் local GenAI assistant.

## Features
- Chat-style Streamlit UI
- Conversation chunking with a bounded recent-context window
- LLM-generated rolling summary memory
- Context-grounded question answering
- Explicit insufficient-context behavior instruction
- Clear-memory control
- Unit tests and Docker setup

## Architecture
User message → chunk store (session state) → Ollama memory summarizer → rolling memory → context-grounded answer → chat UI.

## Stack
Python, Streamlit, Ollama (Qwen 2.5 3B), Requests, Pytest, Docker. Paid API key இல்லை.

## Local setup
```bash
ollama pull qwen2.5:3b
ollama serve
```
புதிய terminal:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
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
docker compose exec ollama ollama pull qwen2.5:3b
```

## Important implementation notes
- The UI stores chunks and memory in Streamlit session state. Restarting the session may clear them.
- Only the latest 40 chunks are retained; memory is an LLM-generated summary and can omit details.
- For production, persist encrypted conversation data, add user authentication, retention controls, token-aware chunking, retrieval indexing, and summary versioning.
- No paid API key is required; downloading the model initially may need internet.
- Never treat generated memory as a perfect transcript or source of truth.
