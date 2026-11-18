# Project 96 — Energy-Efficient LLM System

A local workload benchmarking and energy-estimation dashboard. It measures wall-clock latency and estimates energy from a user-supplied average power reading.

## Features
- Energy calculator (W × seconds → Wh and kWh)
- Repeated workload benchmarking
- Average and p95 latency
- Energy estimate per iteration
- Baseline vs optimized run comparison helper
- JSON report export
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

## Energy formula
`Energy (Wh) = Average Power (W) × Duration (seconds) / 3600`

## Limitations
- The benchmark is a deterministic Python workload, not an LLM inference engine.
- Energy values are estimates using user-supplied average power; wall-clock timing alone cannot measure power consumption.
- For real measurements, use calibrated hardware power telemetry (e.g. device-specific GPU/CPU sensors or an external power meter) and record the measurement method.
- Compare identical prompts, batch sizes, sequence lengths, model versions and hardware settings.
