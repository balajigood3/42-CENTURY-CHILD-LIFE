# Project 11 — Self-Healing RAG System

## நோக்கம்
ஆவணங்களில் இருந்து பதிலுக்கான context-ஐ retrieve செய்து, retrieval பலவீனமாக இருந்தால் query rewrite செய்து மறுமுயற்சி செய்யும் local RAG application.

## Features
- TXT / Markdown document upload
- Local chunking and lexical retrieval
- Retrieval score diagnostics
- Low-score query rewrite with Ollama
- Bounded retry across up to three rewritten queries
- Evidence-grounded answer generation
- Insufficient-context response
- Streamlit UI, pytest suite, Docker

## Architecture
Documents → chunking → local lexical index → top-k retrieval → score check → query rewrite/retry → context-grounded LLM answer.

## Stack
Python, Ollama (Qwen 2.5 3B), Streamlit, Requests, Pytest, Docker. Paid API key இல்லை.

## Run locally
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

## Important limitations
- Retrieval uses normalized lexical token overlap, not semantic embeddings. It is a simple baseline.
- Query rewriting is bounded and may not improve retrieval.
- It does not automatically repair source documents or guarantee complete retrieval.
- For production, replace the baseline with multilingual embeddings + FAISS/Chroma, add document parsing, persistent indexing, access controls, source span citations, and evaluation datasets.
- Initial model download may require internet; no paid API key is used.
