# Project 89 — AI Business Decision Intelligence

A transparent multi-criteria decision support prototype that ranks alternatives using user-defined scores, weights and benefit/cost directions.

## Features
- Compare two or more options
- User-defined decision criteria
- Weighted scoring and normalized weights
- Benefit and cost criteria
- Explainable weighted contributions
- Score gap to runner-up
- Sensitivity analysis across criterion weights
- JSON and Markdown report export
- Streamlit dashboard, pandas, pytest, Docker and Docker Compose
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

## Method
Weighted sum model: normalize criterion weights so they sum to 1, multiply each option score by its normalized weight, reverse cost criteria using `10 - score`, then sum contributions.

## Limitations
- This is a decision-support calculator, not autonomous decision-making or a trained AI model.
- Rankings depend on subjective user-entered scores and weights.
- Sensitivity analysis perturbs one weight at a time and is not a complete uncertainty analysis.
- Hard constraints, dependencies, risk appetite and non-linear trade-offs need separate review.
- Do not use this prototype alone for hiring, credit, medical, legal or other high-impact decisions.
