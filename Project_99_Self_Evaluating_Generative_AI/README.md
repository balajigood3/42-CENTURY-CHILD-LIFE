# Project 99 — Self-Evaluating Generative AI

A local evaluation workbench that scores generated answers against explicit, repeatable test criteria.

## Features
- Batch evaluation using JSON test cases
- Required phrase and forbidden phrase checks
- Expected keyword coverage
- Minimum and maximum word constraints
- Per-case pass/fail and weighted score
- Aggregate pass rate and average score
- Failure category summary
- JSON report download
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

## Test case format
```json
[
  {
    "id": "example-1",
    "answer": "The generated answer to evaluate.",
    "expected_keywords": ["topic", "evidence"],
    "required_phrases": ["required wording"],
    "forbidden_phrases": ["unsupported guarantee"],
    "min_words": 3,
    "max_words": 100
  }
]
```

## Evaluation design and limitations
- This project evaluates observable text rules; it does not prove factual correctness, reasoning quality, fairness or safety.
- Keyword and phrase checks can miss paraphrases and can be fooled by negation or context.
- The weighted score is a configurable heuristic, not a universal quality metric.
- For production, add human-reviewed gold datasets, semantic similarity, factuality/grounding checks, calibrated LLM-as-judge, bias/safety suites, versioned experiments and confidence intervals.
- No model or paid API is required; connect a local model separately if answer generation is needed.
