# Project 69 — Tamil Speech Conversation AI

தமிழ் குரலை உரையாக மாற்றி, local LLM மூலம் பதில் உருவாக்கி, விருப்பமாக பதிலை audio-ஆக மாற்றும் application.

## Features
- Audio upload: WAV, MP3, M4A, WebM, OGG
- Local speech-to-text using faster-whisper
- Tamil-first conversational response using local Ollama
- Optional text-to-speech using pyttsx3 / eSpeak
- Text input fallback
- JSONL conversation history
- Streamlit UI, Docker, pytest
- No paid API keys

## Requirements
Python 3.11, FFmpeg, and (for full conversation) Ollama with a local model.

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
streamlit run app.py
```

The first faster-whisper run may download the selected model weights. Choose `tiny` or `base` for lower resource usage; `small` can provide better recognition at higher memory/compute cost. Set the correct audio language in the UI.

## Docker
```bash
docker compose up --build
```
Open `http://localhost:8501`. Containerized Ollama access requires a reachable host endpoint; `localhost` inside the container refers to the container.

## Tests
```bash
pytest -q
```

## Architecture
Audio upload → faster-whisper transcription → editable text → Ollama chat API → response → optional pyttsx3 speech output → JSONL history.

## Limitations
- This starter accepts uploaded audio; it is not a continuous live microphone streaming system.
- Whisper model weights are downloaded on first use and require disk space and memory.
- pyttsx3 voice and Tamil pronunciation depend on installed system voices; Tamil TTS may not be available on every OS.
- Ollama model responses may be inaccurate; review important information.
- No paid API keys or cloud speech services are used.
