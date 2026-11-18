# Project 15 — Knowledge Conflict Resolution AI

## நோக்கம்
பல ஆவணங்களில் உள்ள கூற்றுகளை ஒப்பிட்டு நேரடி முரண்பாடு, கால/சூழல் வேறுபாடு, பொருந்துதல் அல்லது போதிய தகவல் இல்லாமை என வகைப்படுத்தும் local GenAI app.

## Architecture
TXT/MD upload → Ollama claim extraction → lexical candidate filtering → LLM pair comparison → Markdown report + SQLite history.

## Stack
Python 3.10+, Streamlit, Ollama, Qwen 2.5 3B, SQLite, pytest, Docker. Paid API key தேவையில்லை.

## Setup & Run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
ollama serve
ollama pull qwen2.5:3b
streamlit run app/main.py
```
Open http://localhost:8501. Upload `examples/source_a.txt` and `examples/source_b.txt`.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Container-to-host Ollama connectivity may require configuring the Ollama host for your OS.

## Limitations
- Lexical pre-filter is not semantic retrieval; paraphrased conflicts may be missed.
- LLM extraction/classification may be wrong; confidence is not calibrated.
- Does not determine which source is authoritative or which claim is true. Human review and trusted-source policy are required.
- TXT/Markdown only; PDF, OCR, tables and scanned documents are not included.
