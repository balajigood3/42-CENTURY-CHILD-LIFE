# Project 49 – AI Presentation Generator

Structured text outline-இலிருந்து editable PowerPoint (.pptx) presentation உருவாக்கும் application.

## Features
- Markdown-style outline input.
- Title, agenda, content and closing slides.
- Up to 25 content slides and 8 bullet points per slide.
- Three presentation themes.
- Editable PowerPoint text and shapes.
- PPTX download from Streamlit.
- Dockerfile, Docker Compose and automated tests.
- No paid API keys.

## Architecture
`Text Outline -> Outline Parser -> Slide Model -> PowerPoint Builder -> Editable PPTX`

## Outline format

```text
# Presentation title
## First slide
- First point
- Second point
## Second slide
- Another point
```

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

## Tests

```bash
pytest -q
```

## Output
The generated `.pptx` contains editable text boxes and shapes. Open it in Microsoft PowerPoint, LibreOffice Impress, or another compatible presentation editor.

## Limitations
- Slide content is generated from the supplied outline; this version does not use an LLM to research or invent content.
- Layout is template-based. Very long bullets may need manual adjustment.
- No images, charts, speaker notes, narration, or automatic web research are added in this starter version.
- Review slide content and formatting before presenting.
