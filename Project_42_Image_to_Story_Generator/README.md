# Project 42 — Image-to-Story Generator

Upload an image, obtain an image description through an optional local captioning model, and generate a short story in one of four styles.

## Features
- JPEG, PNG, WEBP upload with size and dimension validation
- Optional BLIP image captioning using a local Transformers model
- Optional OCR fallback for text in images
- Four story styles: adventure, fairy tale, science fiction, mystery
- User-provided story direction
- TXT and JSON downloads
- Streamlit UI, Docker and pytest

## Architecture
`Image Upload → Image Validation → Optional BLIP/OCR Caption → Story Template Engine → TXT/JSON`

## Requirements
Python 3.11+. No paid API keys.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Enable local image captioning (optional)
```bash
pip install transformers torch
```
Select **Use optional local BLIP image captioning model** in the UI. The first run may download model weights. For air-gapped deployment, pre-download and provision the model weights and set `BLIP_MODEL` to the local model directory.

## Enable OCR (optional)
Install `pytesseract` and the Tesseract OCR system binary. OCR is used as a fallback when BLIP is disabled or unavailable.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
The default image is lightweight and does not include the optional BLIP model or Tesseract binary.

## Limitations
- Without BLIP, image description is limited to dimensions and optional OCR; the app cannot infer objects or scene semantics from pixels.
- Story generation uses local templates, not a generative language model.
- BLIP captions may be inaccurate; review them before relying on the resulting story.
- Optional model weights may require an initial download; no paid API is used.
