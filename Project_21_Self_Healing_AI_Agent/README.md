# Project 21 — Self-Healing AI Agent

## நோக்கம்
Task-ஐ சிறிய tool steps ஆக மாற்றி, allowlist செய்யப்பட்ட local tools மூலம் execute செய்து, failure ஏற்பட்டால் வரையறுக்கப்பட்ட retry முயற்சிகளைச் செய்யும் பாதுகாப்பான agent.

## Architecture
`User Task → Planner (Ollama / deterministic fallback) → Tool Allowlist → Execute → Observe → Bounded Retry → Result + Logs`

## Features
- Local Ollama planner (default model: `qwen2.5:3b`)
- Ollama இல்லாவிட்டாலும் demo செய்ய deterministic fallback
- Calculator, uppercase, word count, workspace file read/write tools
- Workspace path traversal protection
- Tool allowlist; arbitrary shell execution இல்லை
- Maximum 5 attempts, maximum 10 planned steps
- Execution logs மற்றும் pytest tests
- Dockerfile + Docker Compose (Ollama உட்பட)

## Requirements
- Python 3.11+
- Docker Desktop / Docker Engine (container வழி இயக்க விரும்பினால்)
- Ollama local model: `qwen2.5:3b` (LLM planning விருப்பத் தேர்வு)

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

Without downloading a model, turn off “Use local Ollama planner”; deterministic examples still work.

## Tests
```bash
pytest -q
```

## Sample tasks
- `calculate 12 * 4`
- `uppercase: hello world`
- `count words: local agent demo`

## Safety & limitations
- This is a bounded workflow agent, not an unrestricted autonomous computer agent.
- It never runs shell commands or arbitrary generated Python.
- File tools are restricted to the `workspace/` directory.
- The retry mechanism retries the same validated call; it does not rewrite code or guarantee that a failed external action can be repaired.
- LLM-generated plans are untrusted and each call is checked against the tool allowlist.
- Local model output may be inaccurate; review actions and logs before using results in production.
- Python-level time checks cannot interrupt a blocked tool mid-call; HTTP planning has a network timeout.
