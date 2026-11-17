# Project 3 – Multi-Step Reasoning AI System

## தமிழ் விளக்கம்
பெரிய கேள்வி அல்லது பிரச்சினையை சிறிய துணைப் பணிகளாகப் பிரித்து, அவற்றை வரிசையாக Local LLM மூலம் தீர்த்து, முடிவுகளை ஒருங்கிணைத்து, இறுதி பதிலை மதிப்பாய்வு செய்யும் Generative AI application.

## Features
- LLM-based task planning and decomposition
- Sequential subtask solving with previous results as context
- Final answer synthesis
- Separate review step and bounded revision loop
- Streamlit interface
- SQLite run history
- Unit tests and Dockerfile
- Paid API key தேவையில்லை

## Requirements
- Python 3.10+
- Ollama
- Local model இயங்குவதற்கான போதுமான RAM / CPU / GPU

## Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull qwen2.5:3b
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

Ollama service இயங்குவதை உறுதிசெய்யவும். App-ல் பிரச்சினை மற்றும் விருப்பமான context உள்ளிட்டு "பகுத்து தீர்வு உருவாக்கு" என்பதை அழுத்தவும்.

## Tests
```bash
pytest -q
```

## Docker
Ollama host machine-ல் இயங்க வேண்டும். Container-க்கு அணுகக்கூடிய Ollama URL அமைக்கவும்:
```bash
docker build -t multi-step-reasoning-ai .
docker run --rm -p 8501:8501 \
  -e OLLAMA_URL=http://host.docker.internal:11434/api/generate \
  multi-step-reasoning-ai
```
Linux-ல் தேவைக்கேற்ப `--add-host=host.docker.internal:host-gateway` சேர்க்கவும்.

## Limitations
- LLM decomposition அல்லது subtask answers தவறாக இருக்கலாம்.
- Review model அதே model family-ஐப் பயன்படுத்துவதால் சுயாதீன சரிபார்ப்பு அல்ல.
- External facts-க்கு trusted sources / RAG சேர்க்க வேண்டும்.
- இது private chain-of-thought-ஐ வெளிப்படுத்தாது; பயனுள்ள சுருக்கமான விளக்கப் படிகளை மட்டுமே வழங்குகிறது.
- High-stakes decisions-க்கு human review அவசியம்.
