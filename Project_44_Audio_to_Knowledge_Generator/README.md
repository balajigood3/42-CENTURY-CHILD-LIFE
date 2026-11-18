# Project 44 – Audio-to-Knowledge Generator

Audio-விலிருந்து transcript உருவாக்கி, அதை summary, key points, action items, terms மற்றும் FAQ candidates ஆக மாற்றும் local-first Streamlit application.

## Features
- WAV, MP3, M4A, OGG, FLAC upload; 50 MB limit.
- Optional offline transcription using `faster-whisper` (CPU, tiny/base/small).
- Transcript edit/paste support when transcription is unavailable or needs correction.
- Structured knowledge extraction and JSON / Markdown downloads.
- Input validation and automated tests.
- Dockerfile and Docker Compose included.
- No paid API key.

## Architecture
`Audio upload -> Validation -> faster-whisper -> Editable transcript -> Knowledge extraction -> JSON/Markdown export`

Knowledge extraction currently uses deterministic sentence and keyword heuristics. It is intentionally lightweight and does not claim semantic understanding equivalent to a large language model.

## Run locally
Python 3.11 is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

The first transcription may download the selected Whisper model. This requires internet access once; inference runs locally afterward. For transcript-only workflows, paste text without installing or downloading a model.

## Run with Docker

```bash
docker compose up --build
```

Open `http://localhost:8501`. The `models` volume retains downloaded model files.

## Tests

```bash
pytest -q
```

## Example input
"Project Atlas starts Monday. We need to review the dataset. Please send the report to Priya by Friday."

## Expected output
- Summary: first few sentences.
- Key points: sentence-level extraction.
- Action items: sentences containing action-oriented phrases.
- Terms: simple capitalized-term extraction.
- FAQ candidates: questions generated from selected sentences.

## Limitations
- Transcription quality depends on audio clarity, language, and model size.
- `faster-whisper` and FFmpeg are needed for audio transcription; install instructions are shown if the optional package is unavailable.
- Whisper model weights are downloaded on first use and are not bundled in this ZIP.
- Heuristic knowledge extraction can miss implicit actions or incorrectly identify terms. Review the editable transcript and generated results before relying on them.
- This demo has no user authentication or persistent database.
