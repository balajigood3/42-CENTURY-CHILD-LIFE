# Project 24 — AI Project Builder Agent

## நோக்கம்
Plain-language project specification-ஐப் பெற்று, Python starter project-க்கான files, README, tests, Dockerfile மற்றும் Docker Compose உருவாக்கும் local AI project builder.

## Architecture
`Project Specification → Ollama JSON Generation → Allowlisted File Validation → Workspace Write → Manifest`

Ollama கிடைக்காவிட்டால் deterministic safe templates பயன்படுத்தப்படும்.

## Features
- Project name மற்றும் description input
- Local Ollama + Qwen 2.5 3B மூலம் starter code generation
- Strict allowlist செய்யப்பட்ட 7 output files
- Template fallback mode
- Duplicate project name rejection
- Generated project manifest
- Generated code தானாக execute செய்யப்படாது
- Streamlit UI, pytest, Dockerfile, Docker Compose

## Local setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
streamlit run app/ui.py
```
Open `http://localhost:8501`.

## Docker setup
```bash
docker compose up --build -d
docker compose exec ollama ollama pull qwen2.5:3b
```
Open `http://localhost:8501`.

## Tests
```bash
pytest -q
```

## Generated files
Projects are written under `generated_projects/<project-slug>/`. Each generated project contains README, requirements, main.py, tests, Dockerfile, docker-compose.yml and project_manifest.json.

## Safety and limitations
- Generated code is untrusted; inspect it before running.
- The builder never executes generated code or shell commands.
- This is a starter-project generator, not a production-grade full-stack code generator.
- Model output can be incomplete or incorrect; template fallback is intentionally minimal.
- No paid API keys are used. Ollama inference runs locally.
