# Project 47 – Visual Question Answering AI

படத்தை upload செய்து அதைப் பற்றிய கேள்விகளைக் கேட்க உதவும் local-first Visual Question Answering application.

## Features
- PNG, JPG, JPEG, WEBP, BMP upload; 15 MB limit.
- Optional semantic VQA using Salesforce BLIP VQA base through Hugging Face Transformers.
- Local CPU inference; no paid API key.
- Basic mode reports dimensions, aspect ratio and average color statistics.
- Streamlit image preview and answer display.
- Dockerfile, Docker Compose and pytest tests.

## Architecture
`Image Upload -> Validation -> BLIP VQA (optional) / Basic Image Analysis -> Answer + Image Details`

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

## Enable semantic VQA (optional)

Install the model runtime:

```bash
pip install "transformers>=4.40,<5.0" torch
```

Choose **Local BLIP model** or **Automatic** in the app. The `Salesforce/blip-vqa-base` weights are downloaded on first use; after caching, inference runs locally. First download can be large and requires internet access.

## Run with Docker

```bash
docker compose up --build
```

To enable BLIP in the container, add `transformers` and `torch` to `requirements.txt` and rebuild. Mounting `./models` retains Hugging Face cache files.

## Tests

```bash
pytest -q
```

## Example questions
- What is in this picture?
- What color is the car?
- How many people are visible?
- What is the person holding?

The semantic questions require BLIP mode. Basic mode only answers image metadata/statistics questions.

## Limitations
- BLIP answers can be wrong, especially for small objects, text, counting, and unusual scenes.
- Basic mode does not understand image semantics; it only reports deterministic image properties.
- The model weights are not bundled in the ZIP.
- This starter app processes one image at a time and does not persist uploads.
- Review model-generated answers before using them in important decisions.
