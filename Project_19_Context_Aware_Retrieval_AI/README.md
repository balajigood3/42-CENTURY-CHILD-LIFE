# Project 19 — Context-Aware Retrieval AI

## நோக்கம்
பயனரின் தற்போதைய கேள்வி, முந்தைய உரையாடல், மற்றும் ஆவண metadata ஆகியவற்றை இணைத்து பொருத்தமான passages-ஐ retrieve செய்து, ஆதாரங்களுடன் பதிலளிக்கும் RAG பயன்பாடு.

## Architecture
TXT/Markdown upload → metadata-aware chunking → SQLite persistence → current-query + conversation-context retrieval → optional LLM query expansion → Ollama answer generation with source citations.

## முக்கிய அம்சங்கள்
- Chunking with source/category metadata
- SQLite persistent document chunks
- Conversation history-aware retrieval for follow-up questions
- Optional Ollama query rewriting to resolve references
- Category and source filters
- Source-grounded answer generation
- Clear conversation context control

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
Open http://localhost:8501. Example files are in `examples/`.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Configure the Ollama host address in the UI if the container cannot reach the host service.

## Limitations
- Retrieval is lightweight lexical token overlap, not a neural embedding or production hybrid search engine.
- Query expansion may fail if Ollama is unavailable; the system falls back to the original query.
- Conversation context can introduce irrelevant terms; keep the chat history focused or clear it.
- Only UTF-8 TXT/Markdown is supported; no PDF parsing, OCR, tables, or image ingestion.
- This is a local single-user prototype; no authentication or multi-user isolation is included.
