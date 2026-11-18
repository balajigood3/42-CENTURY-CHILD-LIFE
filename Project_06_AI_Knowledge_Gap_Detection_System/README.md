# AI Knowledge Gap Detection System

A local-first application that reviews supplied text and identifies missing, underspecified, or unsupported information. It uses Ollama with Qwen 2.5 3B, Streamlit, and SQLite.

## Features
- Tamil-friendly Streamlit interface
- Goal-aware knowledge-gap review
- Structured JSON output: summary, strengths, gaps, priority, resolution question, evidence needed
- SQLite analysis history
- Basic heuristic fallback when Ollama is unavailable
- Unit tests and Docker setup

## Architecture
`Browser -> Streamlit UI -> KnowledgeGapAnalyzer -> Ollama local model -> JSON normalization -> SQLite history`

If Ollama cannot be reached, a small keyword-based fallback is used. The UI identifies this fallback explicitly; it is not a semantic substitute for the LLM.

## Requirements
- Python 3.10+
- Ollama installed locally
- Internet may be needed once to download the open model; no paid API key is used.

## Run locally
```bash
# 1. Download and start the model
ollama pull qwen2.5:3b
ollama serve

# 2. In another terminal, from this folder
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt

# 3. Start the application
streamlit run app.py
```
Open the local URL printed by Streamlit (normally http://localhost:8501).

## Run tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Then pull the model inside the Ollama container:
```bash
docker compose exec ollama ollama pull qwen2.5:3b
```
Open http://localhost:8501.

## Example input
Goal: Review a software project proposal.

Text: "The application stores customer records and provides a dashboard. It will be launched next month."

Possible gaps include access controls, data retention, backup/recovery, performance targets, ownership, test plan, and launch acceptance criteria. Actual findings depend on the model and the supplied text.

## API / programmatic use
```python
from src.analyzer import KnowledgeGapAnalyzer
analyzer = KnowledgeGapAnalyzer()
result = analyzer.analyze("Project description...", "Security review")
print(result)
```

## Limitations and responsible use
- A gap is relative to the supplied text and stated goal; the system cannot know what exists outside the excerpt.
- LLM results can be incomplete or incorrect. Verify high-priority findings with domain experts and source documents.
- The heuristic fallback only checks a few keywords and must not be treated as AI reasoning.
- Do not submit confidential or regulated information unless your local data-handling policy permits it.
- No system can guarantee detection of every knowledge gap.
