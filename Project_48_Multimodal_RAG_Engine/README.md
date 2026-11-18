# Project 48 – Multimodal RAG Engine

Text documents மற்றும் image OCR text-ஐ ஒரே knowledge index-ல் சேர்த்து, கேள்விக்கேற்ற evidence-ஐ retrieve செய்யும் RAG starter application.

## Features
- TXT, Markdown, PDF and image uploads.
- PDF text extraction with pypdf.
- Optional image OCR using Tesseract + pytesseract.
- Text chunking with overlap.
- Lexical keyword retrieval with source attribution.
- Evidence-grounded extractive answer assembly.
- Streamlit UI.
- Dockerfile, Docker Compose and tests.
- No paid API keys.

## Architecture
`Text/PDF/Image -> Text Extraction/OCR -> Chunking -> Local Index -> Lexical Retrieval -> Evidence-based Answer`

## Run locally

Python 3.11 recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

## Enable image OCR

Install Tesseract OCR for your operating system and then:

```bash
pip install pytesseract
```

Docker image installs the Tesseract system package. Add `pytesseract` to `requirements.txt` if you want OCR enabled inside Docker.

## Run with Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -q
```

## Important implementation note
This is a multimodal ingestion pipeline where image content is converted to text using OCR. It is not a vision-language embedding system. Retrieval uses transparent lexical token matching rather than a vector database or semantic embedding model. Answers quote retrieved evidence instead of inventing a generative response.

## Limitations
- Image retrieval quality depends on OCR quality; images without readable text may yield no chunks.
- Scanned PDFs may require OCR; pypdf only extracts embedded text.
- Keyword matching can miss semantic matches and synonyms.
- The in-memory index is lost when the app restarts.
- Always verify retrieved passages and source documents.
