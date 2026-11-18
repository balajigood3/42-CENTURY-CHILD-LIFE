# Project 51 – Self-Healing Code Agent

Python source code மற்றும் error logs-ஐ ஆய்வு செய்து, பொதுவான பிரச்சினைகளை கண்டறிந்து, வரையறுக்கப்பட்ட safe fixes-ஐ பரிந்துரைக்கும் application.

## Features
- Python source upload or editor input.
- AST-based syntax validation.
- Detection: `== None`, bare `except`, mutable default arguments.
- Error-log hints for common Python exceptions.
- Conservative automatic fixes for `== None`, `!= None`, and bare `except`.
- Syntax validation after applying fixes.
- JSON report and repaired source download.
- Dockerfile, Docker Compose and pytest suite.
- No paid API keys.

## Architecture
`Source + Error Logs -> Input Limits -> AST Analysis -> Issue Detection -> Safe Fix Rules -> Syntax Validation -> Download`

## Run locally

Python 3.11 recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

## Run with Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest -q
```

## Safety design
- Uploaded source is parsed but never executed by this application.
- No shell commands are run on uploaded code.
- Automatic edits are limited to a small set of text transformations.
- The repaired result is parsed again to check syntax.
- Review every suggested fix and run your own tests in a sandbox before deployment.

## Limitations
- This is a deterministic static-analysis and repair assistant, not an autonomous LLM coding agent.
- It does not prove runtime correctness or execute project test suites.
- Regex-based fixes may need manual review in unusual formatting or complex expressions.
- Mutable default arguments are detected but not automatically rewritten because a safe transformation depends on function semantics.
- Error-log hints are heuristic and may not identify the root cause.
