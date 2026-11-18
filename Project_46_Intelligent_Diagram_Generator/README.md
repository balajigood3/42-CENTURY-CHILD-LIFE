# Project 46 – Intelligent Diagram Generator

Plain-language process steps-ஐ flowchart வடிவில் மாற்றி SVG மற்றும் Mermaid source ஆக export செய்யும் application.

## Features
- Multi-line process description input.
- Sequential steps and explicit `A -> B` connections.
- Duplicate node and edge removal.
- SVG diagram preview and download.
- Mermaid source generation and download.
- Safe XML text escaping.
- Node-count limit to keep diagrams manageable.
- Dockerfile, Docker Compose and pytest tests.
- No paid API keys or external model dependency.

## Architecture
`Text Input -> Process Parser -> Node/Edge Graph -> SVG Renderer + Mermaid Export -> Download`

## Input format

Sequential:
```text
Start
Validate request
Process request
Send response
```

Explicit connections:
```text
User request -> Validate
Validate -> Approved
Validate -> Rejected
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

## Limitations
- This is a deterministic parser, not an LLM-based natural-language understanding system.
- It interprets line-separated steps and explicit arrows; complex conditions and nested branches should be written explicitly.
- SVG layout is a simple vertical layout. It does not automatically optimize large graph layouts or avoid every crossing.
- Mermaid output can be edited in Mermaid-compatible tools.
