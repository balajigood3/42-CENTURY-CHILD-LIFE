# Project 86 — AI Business Report Generator

Generate a business performance report from structured CSV metrics.

## Features
- CSV upload or paste
- Revenue, expenses, profit and profit margin
- Total orders and average order value
- First-to-last-period percentage change
- KPI dashboard and charts
- Narrative insights and recommendations
- JSON and Markdown report export
- Input validation and sample dataset
- Streamlit, pandas, pytest, Docker and Docker Compose
- No paid API keys

## Required CSV columns
`period,revenue,expenses,orders`

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

## Architecture
CSV input → schema and numeric validation → KPI aggregation → trend calculations → deterministic insight generation → dashboard and report export.

## Limitations
- This is deterministic analytics and template-based narrative generation, not an LLM-powered forecasting system.
- The tool does not infer currency, taxes, accounting policies, seasonality or causal relationships.
- Growth compares only the first and last rows; ensure rows are chronologically ordered.
- Validate data definitions and source quality before using reports for management or financial decisions.
