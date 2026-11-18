# Project 60 — Autonomous DevOps Assistant

Tamil-first project summary: Docker Compose YAML-ஐ static rules மூலம் ஆய்வு செய்து risk report, deployment review plan, checklist உருவாக்கும் கருவி. இது உண்மையான deployment செய்யாது.

## Features
- Docker Compose YAML validation
- Privileged mode, possible inline secrets, image tag, healthcheck, non-root user, restart policy, ports and resource-limit checks
- Streamlit UI and CLI
- JSON risk report, Markdown plan and checklist generation
- Pytest test suite and Docker packaging

## Requirements
- Python 3.11+
- No paid API keys, cloud credentials, or external LLM required

## Local setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI
```bash
python -m devops_assistant.cli sample-compose.yml --output generated
```

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Open http://localhost:8501.

## Architecture
`app.py` (Streamlit UI) / `cli.py` → `generator.py` → `analyzer.py` → JSON + Markdown artifacts.

## Safety and limitations
- Analyzer is static and rule-based; it does not execute YAML commands or user-supplied shell commands.
- Findings can include false positives/negatives and are not a security certification.
- `deploy.resources` behavior depends on the Compose/runtime implementation.
- Review all generated artifacts and use your approved CI/CD process. No production change is performed.
