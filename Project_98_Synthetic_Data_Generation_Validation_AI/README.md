# Project 98 — Synthetic Data Generation & Validation AI

A schema-driven synthetic tabular data generator with deterministic seeds, validation and data profiling.

## Features
- Define integer, float, category and boolean columns
- Generate up to 100,000 synthetic rows
- Reproducible generation with random seed
- Schema and value validation
- Missing/extra column detection
- Numeric and categorical profiling
- CSV and JSON report export
- Streamlit, pandas, pytest, Docker and Docker Compose
- No paid API keys

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open `http://localhost:8501`.

## Docker
```bash
docker compose up --build
```

## Tests
```bash
pytest -q
```

## Schema example
```json
[
  {"name":"age","type":"integer","min":18,"max":80},
  {"name":"segment","type":"category","values":["A","B","C"]},
  {"name":"active","type":"boolean"}
]
```

## Limitations and privacy
- This generator samples independent columns uniformly; it does not learn real-world distributions or correlations.
- Synthetic data is not automatically anonymous or differentially private.
- Do not use generated records as a substitute for privacy review, consent, or access controls.
- For realistic data, add fitted distributions, dependency models, utility metrics, privacy attack testing and domain validation.
