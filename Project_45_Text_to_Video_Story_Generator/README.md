# Project 45 – Text-to-Video Story Generator

உரை வடிவிலான கதையை scene-களாகப் பிரித்து, ஒவ்வொரு scene-க்கும் visual title/caption card உருவாக்கி MP4 video-ஆக export செய்யும் local application.

## Features
- Story text input and automatic sentence-based scene splitting.
- Up to 8 scenes in the Streamlit interface.
- Four visual themes: Midnight, Sunrise, Forest, Ocean.
- Configurable scene duration.
- MP4 preview and download.
- Local rendering with Pillow and imageio/FFmpeg.
- Dockerfile, Docker Compose and pytest suite.
- No paid API keys.

## Architecture
`Story Input -> Scene Parser -> Frame Renderer -> MP4 Encoder -> Preview / Download`

This project generates caption-card videos. It does not generate photorealistic AI footage, character animation, or voice narration. Those capabilities would require additional models/services.

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

## Run with Docker

```bash
docker compose up --build
```

Open `http://localhost:8501`.

## Tests

```bash
pytest -q
```

## Example input

"A young inventor finds a mysterious map. She follows its clues through an old forest. At the final landmark, she discovers a forgotten library."

Expected storyboard: three scenes, each rendered as a themed caption card in the MP4.

## Limitations
- Scene splitting is sentence-based; it does not infer cinematic shot boundaries.
- Visuals are gradient backgrounds and text overlays, not generated images or animated scenes.
- No audio narration or soundtrack is included.
- Long text may wrap into many lines; concise scene text produces better layouts.
- MP4 encoding requires FFmpeg support provided through imageio-ffmpeg and the Docker image.
