# Project 58 — AI API Generator

## தமிழ் விளக்கம்
JSON API specification-ஐ validate செய்து, FastAPI CRUD starter project-ஐ உருவாக்கும் local generator. API key அல்லது paid LLM தேவையில்லை; predictable code generation பயன்படுத்தப்படுகிறது.

## Features
- Resource name, endpoint, fields, types, required flags, HTTP methods validation.
- FastAPI route and Pydantic model generation.
- Streamlit UI and command-line interface.
- Generated source preview and downloadable ZIP.
- Generated project includes Dockerfile, Docker Compose, requirements, README and original spec.
- Unsafe/unsupported identifiers, path traversal-like endpoint patterns, duplicate/reserved fields and unsupported methods rejected.

## Architecture
`JSON API Spec → Validator → FastAPI + Pydantic Code Generator → ZIP Export`

## Local setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## CLI
Create a JSON file (see `examples/product-api.json`) and run:
```bash
python -m api_generator.cli examples/product-api.json --out generated_api.zip
```

## Generated API quick start
After extracting the generated ZIP:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://localhost:8000/docs.

## Tests
```bash
pytest -q
```

## Docker
For the generator UI:
```bash
docker compose up --build
```
For each generated API, use its own included Dockerfile and Compose file.

## Limitations
- The starter uses an in-memory dictionary; data resets on restart.
- This deterministic generator is spec-driven, not a free-form natural-language coding agent.
- Authentication, authorization, persistent database, migrations, rate limiting, and production hardening must be added before production use.
- Generated code should be reviewed and tested before deployment.
