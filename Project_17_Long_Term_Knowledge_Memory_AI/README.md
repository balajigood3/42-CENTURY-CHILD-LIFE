# Project 17 — Long-Term Knowledge Memory AI

## நோக்கம்
பயனர் வழங்கும் குறிப்புகளில் இருந்து நீண்டகாலத்திற்கு பயன்படும் தகவல்களை உள்ளூர் LLM மூலம் பிரித்தெடுத்து, பயனர் ஒப்புதலுடன் SQLite-ல் சேமித்து, பின்னர் தொடர்புடைய கேள்விகளுக்கு அந்த memory-ஐ retrieve செய்து பதிலளிக்கும் பயன்பாடு.

## Architecture
User notes → Ollama memory extraction → user review/approval → SQLite memory store → lexical relevance retrieval → Ollama answer generation. Memory-ஐ deactivate அல்லது நிரந்தரமாக delete செய்யும் controls உள்ளன.

## Stack
Python 3.10+, Streamlit, Ollama (Qwen 2.5 3B), SQLite, pytest, Docker. Paid API key தேவையில்லை.

## Setup
```bash
ollama serve
ollama pull qwen2.5:3b
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```
Open http://localhost:8501. Example notes: `examples/sample_notes.txt`.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
The app uses local SQLite in `data/`. Configure Ollama host connectivity if needed.

## Privacy and limitations
- Memory is stored locally in SQLite; protect the machine and database file.
- Do not enter passwords, API keys, or sensitive personal information.
- Review extracted memories before saving; model extraction may be incomplete or incorrect.
- Retrieval is lexical matching, not semantic/vector search; paraphrased queries may miss memories.
- The model may use stale or incorrect memories; verify important information.
- This prototype does not synchronize across devices or implement multi-user authentication.
