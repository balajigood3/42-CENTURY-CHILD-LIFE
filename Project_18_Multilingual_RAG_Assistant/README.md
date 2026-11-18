# Project 18 — Multilingual RAG Assistant

## நோக்கம்
பல மொழிகளில் உள்ள TXT/Markdown ஆவணங்களை index செய்து, பயனர் தமிழ் அல்லது பிற மொழிகளில் கேள்வி கேட்டால் தொடர்புடைய passages-ஐ retrieve செய்து, அதே மொழியில் grounded answer உருவாக்கும் RAG பயன்பாடு.

## Architecture
Document upload → Unicode character n-gram TF-IDF indexing → cross-language passage retrieval → local Ollama LLM → answer with source filename citations.

## Supported language handling
Tamil, Hindi/Devanagari, Telugu, Kannada, Malayalam, Bengali, Gujarati, Punjabi, Urdu-script and English/Latin-script detection hints. Other languages may work for retrieval but detection is approximate. User can select answer language manually.

## Stack
Python 3.10+, Streamlit, scikit-learn, Ollama (Qwen 2.5 3B), pytest, Docker. No paid API keys.

## Setup & Run
```bash
ollama serve
ollama pull qwen2.5:3b
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
```
Open http://localhost:8501. Try `examples/tamil_knowledge.txt` and `examples/english_knowledge.txt`.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```
Run Ollama on the host and configure its host address in the app if required.

## Limitations
- Retrieval uses character n-gram TF-IDF, not multilingual neural embeddings; semantic paraphrases may be missed.
- Script-based language detection is approximate; code-mixed text and related scripts can be misclassified.
- The LLM may generate unsupported claims; verify cited passages.
- Only UTF-8 TXT/Markdown is supported. PDF parsing, OCR, tables, speech and image input are not included.
- Large document collections may require a persistent vector database and optimized indexing.
