# Project 14 — Intelligent PDF Understanding AI

## நோக்கம்
PDF ஆவணங்களிலிருந்து text மற்றும் page metadata-ஐ extract செய்து, தொடர்புடைய பக்கங்களைத் தேடி, page-level source references உடன் கேள்விகளுக்குப் பதிலளிக்கும் local GenAI system.

## Features
- Multiple PDF upload
- PyMuPDF text extraction
- Page number and PDF metadata retention
- Page-level lexical retrieval
- Evidence-grounded Q&A with filename/page citation instructions
- Insufficient text-match handling
- Streamlit interface, pytest suite, Docker setup

## Architecture
PDF upload → PyMuPDF page extraction → page-level index in session memory → lexical retrieval → Ollama answer with page context.

## Stack
Python, PyMuPDF, Ollama (Qwen 2.5 3B), Streamlit, Pytest, Docker. Paid API key இல்லை.

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
- Text-based PDFs are supported. Scanned/image-only PDFs require OCR, which is not included.
- Retrieval is lexical token overlap, not semantic embeddings.
- Very large PDFs may require memory optimization and page batching.
- The LLM can produce incorrect answers or citations; verify every citation against the displayed extracted page.
- For production, add OCR (e.g. Tesseract), layout/table extraction, embeddings + vector search, persistent document indexing, access controls, and source-span validation.
- Initial model download may require internet; inference is local and requires no paid API key.
