# Project 23 — Multi-Agent Problem Solver

## நோக்கம்
ஒரு சிக்கலை நான்கு specialist roles மூலம் அணுகுதல்: Planner, Analyst, Critic, Coordinator. ஒவ்வொரு agent-ன் output அடுத்த கட்டத்திற்கு context ஆக அனுப்பப்படும்.

## Architecture
`User Problem → Planner → Analyst → Critic → Coordinator → Final Solution + Agent Report`

## Features
- நான்கு specialist agent roles கொண்ட fixed orchestration workflow
- Local Ollama + Qwen 2.5 3B
- Ollama இல்லாமல் இயங்க template fallback mode
- Streamlit UI மற்றும் JSON report download
- pytest tests
- Dockerfile + Docker Compose + Ollama service
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

## Sample problem
"How can a small team reduce customer support response time without increasing headcount?"

## Limitations and safety
- This is a fixed four-role orchestration demo, not a self-directed swarm.
- The roles are sequential prompts to one local model; they are not four separately trained models.
- Outputs may contain mistakes or unsupported assumptions. Validate recommendations before acting.
- The fallback mode is a generic template and does not reason over domain-specific facts.
- No tools that execute arbitrary shell commands or modify external systems are enabled.
