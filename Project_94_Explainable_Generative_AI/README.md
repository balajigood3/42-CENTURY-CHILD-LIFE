# Project 94 — Explainable Generative AI

A transparent text-priority classifier that reports the weighted keyword features contributing to each prediction.

## Features
- Explainable keyword-weight scoring
- Feature-level contribution table
- Top contributing features
- Unmatched-token visibility
- Adjustable decision threshold
- Threshold sensitivity comparison
- JSON explanation export
- Streamlit UI, pytest, Docker and Docker Compose
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

## How it works
Each known token contributes a configured numeric weight. Contributions are summed and compared with a user-selected threshold to produce `priority` or `normal`. Every matched token and weight is returned.

## Limitations
- This is a rule-based explainability baseline, not a generative model or LLM.
- The explanation is a faithful description of the implemented scoring rule, not a causal explanation of language meaning.
- Negation, context, sarcasm, multilingual text and unseen vocabulary are not understood.
- Do not use this toy classifier for consequential decisions without domain validation, bias testing and human review.
