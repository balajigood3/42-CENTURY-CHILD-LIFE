# Project 95 — AI Bias Detection & Mitigation

A fairness-audit prototype for binary classification outputs. It calculates group-wise selection rates, true-positive rates, false-positive rates and accuracy, then suggests human-led mitigation experiments.

## Features
- CSV upload for group, actual and predicted columns
- Group-wise selection rate, TPR, FPR and accuracy
- Disparity gap calculations
- Configurable descriptive warning threshold (0.10 in this version)
- Mitigation experiment suggestions
- JSON report export
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

## CSV example
```csv
group,actual,predicted
Group A,1,1
Group A,0,0
Group B,1,0
Group B,0,1
```

## Metrics
- Selection rate = predicted positives / group size
- TPR = true positives / actual positives
- FPR = false positives / actual negatives
- Accuracy = correct predictions / group size

## Limitations and responsible use
- Group disparities are diagnostic signals, not proof of discrimination or causation.
- Metrics can be unstable with small samples, missing labels or imbalanced groups.
- Fairness definitions may conflict; legal and domain context is essential.
- Use only lawfully collected and appropriately governed audit data.
- This project does not infer protected attributes, alter predictions, or make automated decisions.
- Review mitigation experiments on held-out data with qualified stakeholders before deployment.
