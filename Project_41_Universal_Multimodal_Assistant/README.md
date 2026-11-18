# Project 41 — Universal Multimodal Assistant

A local multimodal intake application for text, PDF, image, and audio files. It extracts available text/metadata and produces a compact preview without calling a paid API.

## Features
- Text input and text-file extraction
- PDF text extraction (first 30 pages)
- Image metadata extraction; optional OCR through Tesseract
- WAV metadata extraction; optional speech transcription through faster-whisper
- 15 MB upload limit and supported-format validation
- JSON result download, Streamlit UI, Docker and pytest

## Architecture
`Text / PDF / Image / Audio → Modality Router → Local Extractor → Unified Result JSON`

## Requirements
Python 3.11+. No paid API keys or hosted model required.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Optional image OCR
Install `pytesseract` with pip and install the Tesseract OCR engine for your operating system. Without these, the app still reads image dimensions and format.

## Optional audio transcription
Install `faster-whisper`. The first transcription may download the small Whisper model weights. For offline-only deployments, provision model weights in advance and disable network access after setup.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Optional OCR/transcription system dependencies are not included in the minimal Docker image.

## Limitations
- This is a modality ingestion and extraction demo, not a general-purpose vision-language model.
- Image understanding is limited to metadata and optional OCR; it does not describe objects or scenes.
- Audio understanding is limited to WAV metadata unless optional speech transcription is installed.
- Scanned PDFs may require a separate OCR pipeline.
- Local extraction previews are not factual verification.
