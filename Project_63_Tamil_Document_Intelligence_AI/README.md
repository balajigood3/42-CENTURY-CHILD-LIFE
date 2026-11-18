# Project 63 — Tamil Document Intelligence AI

தமிழ் மற்றும் பல்மொழி ஆவணங்களை upload செய்து text extract, language detect, keyword extraction, chunking, extractive summary, document-grounded search செய்யும் பயன்பாடு.

## Supported formats
- TXT / Markdown
- DOCX (paragraphs and tables)
- PDF (text-based PDFs; scanned image PDFs need OCR, not included here)

## Features
- Tamil / English / mixed-language detection
- Text chunking with overlap
- Keyword extraction
- Query-based retrieval over document chunks
- Extractive summary
- Streamlit interface
- CLI-ready Python package functions, pytest tests, Docker

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
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
```

## Architecture
Upload → `extractor.py` → `analysis.py` (language detection, chunking, keywords, retrieval, extractive summary) → `assistant.py` → Streamlit UI.

## Limitations
- Retrieval uses token overlap, not semantic embeddings or a vector database.
- Summary is extractive, not LLM-generated.
- Scanned PDFs require OCR and are not supported in this version.
- DOCX/PDF extraction quality depends on source formatting and embedded text.
- Results are not legal/medical advice; verify important content.
- No paid API keys are used.
