# Project 26 — AI Decision Support Agent

## நோக்கம்
பல decision options-ஐ user-defined criteria மற்றும் weights அடிப்படையில் மதிப்பிட்டு, transparent weighted ranking உருவாக்கி, local LLM மூலம் trade-offs மற்றும் uncertainty விளக்குதல்.

## Architecture
`Problem + Options + Criteria → User Ratings → Weighted Scoring → Ollama Explanation → Decision Report`

## Features
- 2–8 decision options
- 1–10 evaluation criteria
- User-defined criterion weights
- 1–5 user ratings
- Deterministic weighted-sum scoring
- Local Ollama + Qwen 2.5 3B explanation
- Offline mode
- JSON report download
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

## Sample
Problem: Choose a project management tool.
Options: Tool A, Tool B, Tool C.
Criteria: Cost 30, Ease of use 25, Features 25, Privacy 20.
Rate each option from 1 (low) to 5 (high).

## Limitations and safety
- Scores are only as reliable as the ratings and weights entered by the user.
- Weighted sum can hide important non-compensatory constraints; add hard constraints separately for real decisions.
- The LLM explains computed results but must not alter the numeric scores.
- The system is decision support, not an automated authority. Human review is required.
- No paid API keys; inference is local through Ollama.
