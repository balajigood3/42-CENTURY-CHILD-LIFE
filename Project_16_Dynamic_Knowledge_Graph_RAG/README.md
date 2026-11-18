# Project 16 — Dynamic Knowledge Graph RAG

## நோக்கம்
ஆவணங்களில் இருந்து entities மற்றும் அவற்றுக்கிடையிலான relationships-ஐ எடுத்து, புதுப்பிக்கக்கூடிய Knowledge Graph உருவாக்கி, graph neighbourhood அடிப்படையில் தொடர்புடைய தகவல்களை retrieve செய்து கேள்விகளுக்கு பதில் தரும் RAG அமைப்பு.

## Architecture
Document upload → Ollama structured extraction → NetworkX entity/relation graph → SQLite persistence → query entity matching → neighbourhood traversal → graph-grounded LLM answer with source names.

## Stack
Python 3.10+, Streamlit, Ollama (Qwen 2.5 3B), NetworkX, SQLite, pytest, Docker. Paid API key தேவையில்லை.

## Setup
Install Ollama, then:
```bash
ollama serve
ollama pull qwen2.5:3b
python -m venv .venv
# Windows: .venv\Scripts\activate
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
Configure Ollama host connectivity for your environment if the container cannot reach the host service.

## Features
- Ingest multiple TXT/Markdown files and update a named document's graph.
- Entity deduplication by normalized/stable entity ID returned by the model.
- Multi-edge directed graph retains relation evidence and source document.
- SQLite persistence across restarts.
- Graph neighbourhood retrieval and source-aware answer prompt.
- Export graph as GraphML.

## Limitations
- Entity resolution depends on LLM-generated IDs; aliases may become duplicate nodes.
- Retrieval uses lexical entity-name/description overlap plus graph traversal, not embedding search.
- LLM extraction can omit or hallucinate relations; evidence snippets should be checked against originals.
- Only TXT/Markdown text is supported; no PDF parsing, OCR, tables, or image ingestion.
- This is a local prototype, not a production multi-user graph database. Review sensitive documents before processing.
