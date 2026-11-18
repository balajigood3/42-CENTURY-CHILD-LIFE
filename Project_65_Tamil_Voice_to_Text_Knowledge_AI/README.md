# Project 65 — Tamil Voice-to-Text Knowledge AI

தமிழ் audio பதிவுகளை local Whisper மூலம் text-ஆக மாற்றி, keywords/key points உருவாக்கி, பின்னர் transcript-ஐத் தேடக்கூடிய knowledge notes ஆகச் சேமிக்கும் பயன்பாடு.

## Features
- WAV, MP3, M4A, FLAC, OGG audio upload
- Local OpenAI Whisper transcription with Tamil language hint
- Transcript, keyword and key-point extraction
- Search across saved transcript sentences
- JSON knowledge note storage
- Streamlit UI and Docker Compose
- No paid API key

## Requirements
Python 3.11+, FFmpeg, and enough RAM/storage for the chosen Whisper model.

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
Audio upload → local Whisper → transcript → `knowledge.py` → keyword/key-point extraction → JSON storage → sentence search.

## Limitations
- First run may download Whisper model weights; this requires internet access once.
- CPU transcription can be slow; model size affects speed and accuracy.
- Tamil accuracy depends on recording quality, accent, noise, and model.
- Search is keyword overlap, not semantic vector retrieval.
- This application stores transcripts locally; do not upload confidential recordings without authorization.
