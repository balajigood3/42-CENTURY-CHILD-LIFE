# Project 78 — AI Knowledge Tutor

கற்றல் கேள்விகளுக்கு நேரடி பதில், கட்டமைக்கப்பட்ட பாட விளக்கம், முக்கியச் சொற்கள், worked example மற்றும் practice questions வழங்கும் local-first tutor.

## Features
- Topic and learner-question input
- School, Beginner, Intermediate and Advanced levels
- Short, Detailed and Exam-focused lesson styles
- Key concepts and worked example
- Three practice questions with answers and explanations
- Further-study suggestions and caveats
- Structured JSON validation
- Local Ollama (`qwen2.5:3b`) and transparent offline scaffold
- Markdown export and JSONL learning history
- Streamlit UI, Docker, Docker Compose, pytest
- No paid API keys

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
streamlit run app.py
```

## Docker
```bash
docker compose up --build
```
Open `http://localhost:8501`. For AI mode, Ollama must be reachable from the container; container localhost is not the host.

## Tests
```bash
pytest -q
```

## Architecture
Learner question + optional reference notes → prompt builder → local Ollama JSON → schema validation → lesson and practice → history and Markdown export.

## Limitations
- Offline mode is a generic study scaffold and does not answer questions semantically.
- Local model explanations can be incorrect, incomplete, or overconfident; verify important facts with trusted materials.
- Reference notes are context, not independently verified sources.
- This tool is an educational aid, not a substitute for expert instruction in high-stakes domains.
