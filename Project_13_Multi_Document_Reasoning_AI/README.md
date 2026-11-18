# Project 13 — Multi-Document Reasoning AI

## நோக்கம்
இரண்டு அல்லது அதற்கு மேற்பட்ட ஆவணங்களிலிருந்து தொடர்புடைய பகுதிகளை retrieve செய்து, அவற்றின் ஒற்றுமைகள், வேறுபாடுகள், முரண்பாடுகள் மற்றும் தனித்துவமான தகவல்களை ஒருங்கிணைத்து பதிலளித்தல்.

## Features
- Multiple TXT / Markdown uploads
- Per-document chunking
- Per-document lexical retrieval
- Evidence coverage diagnostics
- Cross-document synthesis and comparison prompt
- Source filename references in generated answer
- Conflict-aware instruction
- Streamlit UI, tests, Docker setup

## Architecture
Documents → per-document chunks → query relevance scoring → top-k evidence per document → LLM cross-document synthesis → cited response.

## Stack
Python, Ollama (Qwen 2.5 3B), Streamlit, Requests, Pytest, Docker. No paid API keys.

## Local setup
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
- Retrieval uses lexical token overlap, not semantic embeddings.
- The model only sees retrieved chunks, not necessarily every part of every document.
- Filename citations identify the source document but are not precise page/line citations.
- LLM synthesis can miss conflicts or infer unsupported relationships. Verify conclusions against original documents.
- For production, add multilingual embeddings, vector database, reranking, page/line metadata, structured claim extraction, and evaluation.
- Model download may need internet once; inference is local and does not require a paid API key.
