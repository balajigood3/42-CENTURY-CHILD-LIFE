# Project 20 — Continuous Learning Knowledge AI

## நோக்கம்
புதிய மற்றும் புதுப்பிக்கப்பட்ட ஆவணங்களை incremental-ஆக knowledge base-ல் சேர்த்து, version history பராமரித்து, பயனர் relevance feedback மூலம் எதிர்கால retrieval ranking-ஐ சிறிதளவு மேம்படுத்தும் local GenAI அமைப்பு.

## Architecture
Document upload → content hash/version check → chunking → SQLite versioned storage → lexical retrieval + feedback reranking → Ollama grounded answer → user feedback loop.

## முக்கிய அம்சங்கள்
- Incremental document ingestion
- Duplicate upload detection using SHA-256 content hash
- Per-document version history
- Active version management
- Chunk-level relevance ratings and comments
- Feedback-weighted retrieval ranking
- Source/version citations in answers
- SQLite persistence and Docker deployment

## Stack
Python 3.10+, Streamlit, SQLite, Ollama (Qwen 2.5 3B), pytest, Docker. No paid API key required.

## Setup & Run
```bash
ollama serve
ollama pull qwen2.5:3b
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```
Open http://localhost:8501. Sample documents are in `examples/`.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Configure Ollama host access if the container cannot reach the host service.

## Important distinction
This project does not fine-tune or retrain the LLM. "Continuous learning" here means incremental knowledge-base updates, document versioning, and feedback-based retrieval reranking.

## Limitations
- Retrieval uses lexical token overlap rather than vector embeddings or semantic search.
- User feedback is a small ranking signal and may be biased or noisy.
- The model can still hallucinate; verify answers against cited document versions.
- Only UTF-8 TXT/Markdown is supported; PDF, OCR, tables and images are not included.
- Local SQLite is suitable for a prototype, not high-concurrency enterprise deployment.
