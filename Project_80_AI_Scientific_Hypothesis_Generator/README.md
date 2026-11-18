# Project 80 — AI Scientific Hypothesis Generator

Research observation மற்றும் user-supplied background notes அடிப்படையில் falsifiable candidate hypotheses, null hypotheses, variables, predictions, study design மற்றும் validation plan உருவாக்கும் local-first research assistant.

## Features
- Research field, phenomenon and background evidence input
- Experimental, observational, computational, survey and mixed-method study types
- 1–3 candidate hypotheses with corresponding null hypotheses
- Independent, dependent and control variables
- Measurable predictions and measurement suggestions
- Confounders and ethical considerations
- Confidence labels and validation plan
- Local Ollama (`qwen2.5:3b`) and offline template mode
- Markdown report export and JSONL history
- Streamlit UI, Docker, Docker Compose, pytest
- No paid API keys

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama serve
streamlit run app.py
```

## Docker
```bash
docker compose up --build
```
Open `http://localhost:8501`. Ollama must be reachable from the container for AI mode; container localhost is not the host.

## Tests
```bash
pytest -q
```

## Architecture
Observation + background notes → prompt builder → local Ollama JSON → schema validation → candidate hypotheses → validation plan/report.

## Scientific and ethical limitations
- Generated hypotheses are proposals, not established findings or proof of novelty.
- Validate claims against primary literature and consult domain experts.
- Observational data generally supports association, not causal conclusions.
- Determine sample size and analysis methods before data collection.
- Obtain institutional ethics approval and informed consent where applicable. Do not begin human or animal research based solely on generated suggestions.
- Offline mode is a generic scaffold and does not reason about the supplied science.
