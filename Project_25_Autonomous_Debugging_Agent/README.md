# Project 25 — Autonomous Debugging Agent

## நோக்கம்
Python source code மற்றும் traceback/error log கொடுத்தால் root-cause analysis செய்து, local LLM மூலம் corrected code proposal உருவாக்கி, அதன் Python syntax-ஐ validate செய்யும் debugging assistant.

## Architecture
`Source + Error Log → Ollama Analysis → Proposed Fix → AST Syntax Validation → Unified Diff + Download`

## Features
- Python source மற்றும் traceback input
- Local Ollama + Qwen 2.5 3B
- Root-cause explanation மற்றும் corrected code proposal
- Python AST syntax validation (code execution இல்லை)
- Unified diff generation
- Offline diagnostic fallback
- Streamlit UI, pytest, Dockerfile, Docker Compose
- Paid API key தேவையில்லை

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

## Safety and limitations
- Supplied and generated code is never executed by this application.
- AST parsing checks syntax only; it does not prove correctness or safety.
- Model-generated fixes may be wrong or incomplete. Review the diff and run tests in an isolated development environment.
- Offline mode provides debugging steps only; it does not generate a replacement implementation.
- No paid API keys are used; inference is local through Ollama.
