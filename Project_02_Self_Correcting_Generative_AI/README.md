# Project 2 – Self-Correcting Generative AI System

## நோக்கம்
Local open-source LLM மூலம் பதிலை உருவாக்கி, அதன் தரத்தை மதிப்பிட்டு, கண்டறியப்பட்ட குறைகளைத் திருத்தும் demo application.

## தேவைகள்
- Python 3.10+
- Ollama
- RAM/CPU/GPU திறனுக்கு ஏற்ற local model
- Internet தேவையானது: முதல் முறை Python packages மற்றும் model download செய்ய மட்டும்.

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen2.5:3b
```

Ollama service இயங்குவதை உறுதிசெய்யவும். பின்னர்:
```powershell
streamlit run app.py
```
Browser-ல் Streamlit காட்டும் local URL-ஐ திறக்கவும்.

## Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull qwen2.5:3b
streamlit run app.py
```

## Tests
```bash
pytest -q
```

## Docker
Ollama-வை host machine-ல் இயக்கி, container-க்கு அணுகக்கூடிய Ollama URL அமைக்க வேண்டும்.
```bash
docker build -t self-correcting-ai .
docker run --rm -p 8501:8501 \
  -e OLLAMA_URL=http://host.docker.internal:11434/api/generate \
  self-correcting-ai
```
Linux-ல் தேவைக்கேற்ப `--add-host=host.docker.internal:host-gateway` சேர்க்கவும்.

## முக்கிய வரம்புகள்
- LLM தன்னைத்தானே மதிப்பிடுவதால் அதன் score உண்மைத்தன்மைக்கான உத்தரவாதமல்ல.
- Reference context இல்லாமல் factual correctness-ஐ உறுதிப்படுத்த முடியாது.
- இது demonstration / portfolio project. உயர்-ஆபத்து முடிவுகளுக்கு மனித சரிபார்ப்பு அவசியம்.
- எந்த paid API key-யும் தேவையில்லை. Local model download மற்றும் runtime-க்கு உங்கள் கணினி வளங்கள் தேவை.
