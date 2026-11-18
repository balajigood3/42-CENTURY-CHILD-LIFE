# Project 43 — Video Understanding & Summary AI

A local video inspection and summarization prototype. It reads video metadata, samples keyframes, optionally captions frames with a local BLIP model, and combines captions with an optional user-provided transcript.

## Features
- MP4, MOV, AVI, MKV, WEBM input
- 100 MB upload limit
- Video duration, FPS, frame count, and resolution extraction
- Configurable keyframe sampling (1–12)
- Optional local BLIP frame captioning
- Optional pasted transcript integration
- TXT/JSON summary downloads
- Streamlit UI, Docker, and pytest

## Architecture
`Video Upload → Validation → OpenCV Metadata + Keyframes → Optional BLIP Captions → Summary Builder → Report`

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

## Enable local frame captioning (optional)
```bash
pip install transformers torch
```
Enable BLIP in the UI. The first run may download model weights. For offline deployment, pre-provision the weights and set `BLIP_MODEL` to the local model directory.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Limitations
- Without BLIP, the app extracts metadata and keyframes but does not understand visual events semantically.
- Only sampled frames are analyzed; brief events between samples can be missed.
- Audio is not extracted or transcribed automatically. Paste a transcript if available.
- BLIP captions can be inaccurate and should be reviewed.
- This is a prototype, not a forensic video analysis system.
