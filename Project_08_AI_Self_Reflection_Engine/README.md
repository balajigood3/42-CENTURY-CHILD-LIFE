# Project 8 — AI Self-Reflection Engine

## நோக்கம்
முதலில் ஒரு பதிலை உருவாக்கி, பின்னர் அதன் குறைபாடுகளை விமர்சித்து, மேம்படுத்தப்பட்ட பதிலை வழங்கும் local-first GenAI workflow.

## Workflow
1. Draft generation
2. Critique: correctness, relevance, missing details, unsupported claims, clarity
3. Revision using the critique
4. Configurable 1–3 reflection rounds
5. Final answer and reflection history displayed in Streamlit

## Stack
Python, Ollama (Qwen 2.5 3B), Streamlit, Requests, Pytest, Docker. Paid API key இல்லை.

## Setup
```bash
ollama pull qwen2.5:3b
ollama serve
```
புதிய terminal:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
docker compose exec ollama ollama pull qwen2.5:3b
```

## Architecture
Browser → Streamlit → SelfReflectionEngine → Ollama local model → Draft/Critique/Revision loop → Final answer.

## Python usage
```python
from src.reflection import SelfReflectionEngine
engine = SelfReflectionEngine()
result = engine.run("Explain RAG architecture", rounds=2)
print(result["final_answer"])
```

## Limitations
- The model critiques its own output; this is not independent verification and may preserve its own errors.
- More reflection rounds increase latency and local compute usage.
- No guarantee of factual correctness. Use retrieval, citations, deterministic checks, and human review for high-impact tasks.
- Initial model download may need internet, but no paid API key is used.
