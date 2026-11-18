# Project 50 – Real-Time Multimodal AI Assistant

Text, image மற்றும் audio inputs-ஐ ஒரே workspace-ல் சேர்த்து செயலாக்கும் local-first multimodal assistant starter.

## Features
- Text context and question input.
- Image upload with metadata extraction.
- Optional BLIP image captioning.
- Audio upload with optional faster-whisper transcription.
- Combined context view and Markdown export.
- Streamlit interface.
- Dockerfile, Docker Compose and automated tests.
- No paid API keys.

## Architecture
`Text + Image + Audio -> Validation -> Image Caption / Audio Transcription (optional) -> Context Aggregation -> Response Export`

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

## Optional local model integrations

Image captioning:

```bash
pip install "transformers>=4.40,<5.0" torch
```

Audio transcription:

```bash
pip install faster-whisper
```

Enable the relevant checkboxes in the app. Model weights are downloaded on first use and then run locally. CPU inference may be slow on large files.

## Run with Docker

```bash
docker compose up --build
```

To enable optional models in Docker, add their packages to `requirements.txt` before building. The `models` volume preserves Hugging Face cache files.

## Tests

```bash
pytest -q
```

## Limitations and scope
- This is an upload-and-process multimodal starter, not continuous live audio/video streaming.
- Without optional models, image processing reports metadata and audio remains an attachment; semantic image captioning and speech transcription are not enabled.
- The response layer aggregates source context transparently; it is not an LLM reasoning engine and does not claim to answer arbitrary questions.
- BLIP captions and Whisper transcripts may be inaccurate. Verify important information.
- Uploaded data is processed in the current Streamlit session and is not persisted to a database.
