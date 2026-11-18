# Project 27 — Agent Collaboration Platform

## நோக்கம்
ஒரு team task-ஐ நான்கு specialist agents இடையே பகிர்ந்து, ஒவ்வொரு agent-ன் கருத்தையும் அடுத்த agent-க்கு context ஆக அனுப்பி, ஒருங்கிணைந்த outcome உருவாக்குதல்.

## Architecture
`User Task → Planner → Researcher → Reviewer → Coordinator → Collaboration Report`

## Features
- நான்கு role-based agents
- Sequential context sharing
- Local Ollama + Qwen 2.5 3B
- Offline deterministic template mode
- Agent-by-agent output tabs
- JSON collaboration report download
- Streamlit UI, pytest, Dockerfile, Docker Compose
- No paid API keys

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

## Sample task
"Design a low-cost employee onboarding process for a 30-person startup."

## Limitations and safety
- This is a fixed four-agent sequential workflow, not an unbounded autonomous swarm.
- All four roles use the same local model; they are role prompts, not separate trained models.
- Researcher role identifies research needs; it does not browse the web or verify sources.
- Outputs can contain unsupported assumptions. Validate important claims before action.
- No external tools, shell execution, or automatic changes to business systems are enabled.
