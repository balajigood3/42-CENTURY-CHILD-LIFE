# Project 12 — Autonomous Knowledge Base

## நோக்கம்
பயனர் upload செய்யும் ஆவணங்களை local SQLite knowledge base-ல் index செய்து, புதுப்பிக்கப்பட்ட ஆவணங்களை மீண்டும் index செய்து, கேள்விகளுக்கு தொடர்புடைய passages அடிப்படையில் பதிலளிக்கும் பயன்பாடு.

## Features
- TXT / Markdown upload
- Automatic text chunking
- SQLite document + chunk persistence
- SHA-256 content hash மூலம் duplicate/no-change detection
- ஒரே பெயரில் உள்ள document மாறினால் அதன் chunks update
- Lexical retrieval with top-k
- Source-aware local LLM answer
- Insufficient-knowledge response
- Clear knowledge base control

## Architecture
Upload → content hash → chunking → SQLite knowledge store → lexical top-k search → Ollama answer with source filenames.

## Stack
Python, Streamlit, SQLite, Ollama (Qwen 2.5 3B), Pytest, Docker. Paid API key இல்லை.

## Local setup
```bash
ollama pull qwen2.5:3b
ollama serve
```
மற்றொரு terminal:
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
- Retrieval is lexical token overlap, not semantic vector search.
- Only TXT and Markdown are accepted in this version.
- This is a local personal knowledge base; authentication, multi-user isolation, backups, encryption, and document-level permissions are not implemented.
- LLM may produce incorrect answers; verify important claims against source documents.
- Initial model download may require internet; no paid API key is used.
