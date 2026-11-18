# Project 66 — Indian Language Translation Generator

இந்திய மொழிகளுக்கிடையே local translation workflow. Argos Translate-ன் open-source offline language packages பயன்படுத்தலாம்.

## Supported language catalog
English, Tamil, Hindi, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Urdu, Odia.

## Features
- Source/target language selection
- Long-text chunking
- Optional Argos Translate local inference
- Translation history in JSONL
- Download translated output
- Streamlit UI, Docker, pytest
- No paid API keys

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Install language packages
Argos Translate packages are language-pair specific. Install a compatible source→target package using the Argos package index/CLI before enabling “Use installed Argos Translate model”. Package availability varies by language pair and release.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Architecture
Streamlit UI → text chunking → translation engine → Argos local package (optional) → JSONL history.

## Limitations
- The offline fallback does not translate; it clearly reports that no model is configured.
- A matching Argos model package must be installed for each translation direction.
- Translation quality varies across language pairs, especially low-resource pairs.
- Review legal, medical, financial, and official translations with qualified human translators.
- No paid API key or hosted translation service is required.
