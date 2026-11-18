# Project 70 — Low-Resource Language LLM

குறைந்த அளவு training data கொண்ட மொழிகளுக்கான local multilingual assistant starter. இது model training framework அல்ல; prompt-based local inference, language metadata, script diagnostics, and evaluation scaffolding வழங்குகிறது.

## Supported language choices
Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, English.

## Features
- Language-aware task prompt construction
- Local Ollama inference (`qwen2.5:3b` default)
- Unicode script detection
- Basic output integrity checks and script ratio diagnostic
- JSONL history and output download
- Streamlit UI, Docker, pytest
- No paid API keys

## Setup
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
Open `http://localhost:8501`. If Ollama runs on the host, configure a reachable host address; container `localhost` is not the host.

## Tests
```bash
pytest -q
```

## Architecture
Streamlit UI → Unicode script detector → language/task prompt builder → local Ollama chat API → script/integrity diagnostics → JSONL history.

## Extending for truly low-resource languages
- Collect consented, licensed, representative parallel and monolingual corpora.
- Normalize Unicode carefully and document orthographic conventions.
- Create train/dev/test splits by source document to prevent leakage.
- Evaluate with native-speaker review plus suitable metrics (for translation, chrF/COMET where applicable).
- Consider adapter fine-tuning (LoRA) only after data quality, licensing, and compute requirements are established.

## Limitations
- The default general-purpose model may perform poorly on low-resource languages; selecting a language in the UI does not guarantee fluency.
- Script detection is heuristic and cannot reliably identify a language when scripts are shared (e.g. Hindi and Marathi both use Devanagari).
- Script ratio is not a semantic or translation quality metric.
- This project does not train or fine-tune a new LLM.
- Review important outputs with fluent speakers. No paid API key is required.
