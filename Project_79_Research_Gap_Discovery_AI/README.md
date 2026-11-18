# Project 79 — Research Gap Discovery AI

User-supplied literature notes மற்றும் research question-ஐ வைத்து candidate research gaps, possible research directions, limitations மற்றும் next steps உருவாக்க உதவும் local-first research assistant.

## Features
- Research field and question input
- Paste literature summaries/notes with paper IDs
- Candidate gap classification: theoretical, methodological, empirical, contextual, practical
- Evidence excerpts traceable to supplied notes
- Confidence labels and rationale
- Three possible research directions with objective, method and validation
- Explicit limitations and follow-up literature-search steps
- Local Ollama (`qwen2.5:3b`) and offline note-review mode
- Markdown report export and JSONL history
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
Open `http://localhost:8501`. Ollama must be reachable from the container for AI mode; container localhost is not the host.

## Tests
```bash
pytest -q
```

## Architecture
Research question + literature notes → prompt builder → local Ollama JSON → schema validation → candidate gaps and directions → report/history.

## Important limitations
- This application does not search scholarly databases or verify publication records.
- A candidate gap is not proof of originality or novelty. Conduct a systematic search and consult a supervisor/domain expert.
- LLMs can misinterpret notes or create unsupported hypotheses. Check every evidence statement against the original paper.
- Offline mode only extracts note snippets and provides a review workflow; it does not discover gaps semantically.
