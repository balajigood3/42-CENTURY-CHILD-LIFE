# Project 10 — Reliable Answer Generation AI

## நோக்கம்
கேள்விக்கு பதில் உருவாக்கி, வழங்கப்பட்ட ஆதாரத்துடன் ஒப்பிட்டு, unsupported claims மற்றும் uncertainty-ஐக் குறிப்பிட்டு, திருத்தப்பட்ட பதிலை வழங்கும் local-first GenAI pipeline.

## Pipeline
1. Evidence-aware draft generation
2. LLM audit for unsupported claims and contradictions
3. Deterministic basic checks
4. Revision with uncertainty and evidence constraints
5. Final answer + verification report

## Stack
Python, Ollama (Qwen 2.5 3B), Streamlit, Requests, Pytest, Docker. Paid API key இல்லை.

## Setup
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

## Limitations
- LLM audit is self-review, not independent verification.
- Basic checks detect only simple formatting/absence conditions; they cannot prove factual correctness.
- Reliability depends on the quality and relevance of supplied evidence.
- The app does not currently perform web search or source retrieval.
- For production, add trusted retrieval, source-level citations, claim extraction, independent verification, logging, authentication, and human review.
- Initial model download may require internet; no paid API key is used.
