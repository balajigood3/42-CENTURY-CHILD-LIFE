# Project 59 — AI Database Schema Generator

## தமிழ் விளக்கம்
Structured JSON schema-ஐ validate செய்து SQL DDL, Mermaid ER diagram மற்றும் SQLAlchemy ORM models உருவாக்கும் local tool. Paid API key அல்லது external LLM தேவையில்லை.

## Features
- Multiple table and column definitions.
- Primary key, unique, nullable, default constraints.
- Foreign key validation and DDL generation.
- SQL, Mermaid ERD, SQLAlchemy model generation.
- Streamlit UI and CLI.
- ZIP export with generated artifacts.
- Identifier validation and safe scalar default handling.

## Architecture
`JSON Schema → Validator → SQL/ERD/ORM Generators → ZIP Export`

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
```bash
python -m db_schema_gen.cli examples/shop-schema.json --out database_schema_bundle.zip
```

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Output files
- `schema.sql` — SQL DDL
- `erd.mmd` — Mermaid ER diagram source
- `models.py` — SQLAlchemy declarative models
- `schema.json` — normalized schema
- `README.md` and runtime requirements

## Limitations and safety
- This is deterministic schema generation, not a natural-language reasoning model.
- SQL dialect differences may require manual adjustments.
- Relationships are emitted as foreign-key constraints; ORM relationship properties are not generated.
- Review generated SQL and test migrations against a disposable database before production use.
