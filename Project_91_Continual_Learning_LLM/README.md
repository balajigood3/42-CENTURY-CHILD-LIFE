# Project 91 — Continual Learning LLM

A local incremental text-classification experiment with bounded replay memory and class-centroid updates.

## Features
- Add labeled examples incrementally
- Bounded replay buffer to limit memory use
- Rebuild class prototypes as new examples arrive
- Predict labels using cosine similarity
- Evaluate on JSONL examples
- Export and restore replay memory
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

## JSONL format
One JSON object per line:
```json
{"text":"The invoice is overdue","label":"billing"}
{"text":"API server returned timeout","label":"technical"}
```

## Architecture
`Labeled Examples -> Tokenization -> Replay Buffer -> Vocabulary & Class Centroids -> Cosine Prediction -> Evaluation`

## Limitations
- Despite the project title, this is not a pretrained or fine-tuned LLM; it is a lightweight, inspectable continual-learning baseline.
- Bag-of-words features do not understand semantics, context, or Tamil text.
- Similarity scores are not calibrated probabilities.
- Replay memory is bounded FIFO; older examples may be forgotten.
- For production continual learning, add privacy controls, drift detection, representative replay sampling, robust evaluation and model-version governance.
