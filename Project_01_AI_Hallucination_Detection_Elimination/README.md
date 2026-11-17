# Project 1 – AI Hallucination Detection & Evidence-Based Correction

## தமிழ் விளக்கம்
AI உருவாக்கிய பதிலை atomic claims ஆகப் பிரித்து, பயனர் வழங்கிய reference documents மற்றும் context உடன் ஒப்பிட்டு SUPPORTED / CONTRADICTED / UNKNOWN என வகைப்படுத்துகிறது. பின்னர் ஆதாரத்துடன் பொருந்தும் திருத்தப்பட்ட பதிலை உருவாக்குகிறது.

## Requirements
- Python 3.10+
- Ollama installed and running
- RAM/CPU/GPU வசதிக்கு ஏற்ற local LLM
- முதல் setup-க்கு internet: Python packages, Ollama model, embedding model download செய்ய மட்டும்
- Paid API key தேவையில்லை.

## Windows PowerShell setup
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```
`nomic-embed-text` இந்த project-இன் default embedding model அல்ல; விருப்பமாக பயன்படுத்த விரும்பினால் `EMBEDDING_MODEL`-ஐ மாற்றலாம். Default: `sentence-transformers/all-MiniLM-L6-v2`.

Ollama service இயங்குவதை உறுதி செய்து:
```powershell
streamlit run app.py
```

## Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
streamlit run app.py
```

## Usage
1. Sidebar-ல் TXT அல்லது MD reference documents upload செய்யவும்.
2. கேள்வி மற்றும் சரிபார்க்க வேண்டிய AI பதிலை உள்ளிடவும்.
3. விருப்பமாக கூடுதல் context கொடுக்கவும்.
4. “சரிபார்த்து திருத்து” என்பதை அழுத்தவும்.
5. Claim-level status, retrieved evidence மற்றும் corrected answer பார்க்கவும்.

## Tests
```bash
pytest -q
```

## Docker
Ollama host-ல் இயங்க வேண்டும். Container-ல் Ollama-வை அடையக்கூடிய URL கொடுக்கவும்:
```bash
docker build -t hallucination-detector .
docker run --rm -p 8501:8501 \
  -e OLLAMA_URL=http://host.docker.internal:11434/api/generate \
  hallucination-detector
```
Linux-ல் தேவைக்கேற்ப `--add-host=host.docker.internal:host-gateway` சேர்க்கவும். Sentence Transformers embedding model முதல் முறை download ஆகும்; offline deployment-க்கு முன்கூட்டியே model cache செய்யவும்.

## Important limitations
- Retrieval similarity உண்மைத்தன்மைக்கான சான்றல்ல; LLM claim classification-லும் தவறு இருக்கலாம்.
- Reference documents இல்லாமல் factual verification உறுதி செய்ய இயலாது.
- இது portfolio/research prototype; மருத்துவம், சட்டம், நிதி போன்ற high-stakes பயன்பாடுகளுக்கு நிபுணர் சரிபார்ப்பு அவசியம்.
- இந்த அமைப்பு hallucination-ஐ முழுமையாக நீக்குவதாக உத்தரவாதம் அளிக்காது.
