# Project 5 – Uncertainty-Aware Generative AI System

## தமிழ் விளக்கம்
கேள்விக்கு பதில் உருவாக்கும்போது தகவல் போதுமா, எந்த assumptions பயன்படுத்தப்பட்டன, என்ன தகவல் இல்லை, ஏன் uncertainty உள்ளது என்பதைக் காட்டும் Local Generative AI application.

## Features
- Local LLM answer generation
- LOW / MEDIUM / HIGH / INSUFFICIENT_INFORMATION labels
- Assumption identification and missing-information checklist
- Uncertainty explanation and SQLite history
- Streamlit UI, tests, Docker deployment
- Paid API key தேவையில்லை

## Requirements
Python 3.10+, Ollama, local model இயங்கத் தேவையான RAM / CPU / GPU.

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

Ollama service இயங்குவதை உறுதிசெய்து கேள்வி மற்றும் கிடைக்கும் context-ஐ உள்ளிடவும்.

## Tests
```bash
pytest -q
```

## Docker
Ollama host machine-ல் இயங்க வேண்டும். Container-ல் அணுகக்கூடிய URL அமைக்கவும்:
```bash
docker build -t uncertainty-aware-ai .
docker run --rm -p 8501:8501 -e OLLAMA_URL=http://host.docker.internal:11434/api/generate uncertainty-aware-ai
```
Linux-ல் தேவைக்கேற்ப `--add-host=host.docker.internal:host-gateway` சேர்க்கவும்.

## Limitations
Uncertainty labels qualitative LLM judgments மட்டுமே; calibrated confidence probabilities அல்ல.
Model தன் uncertainty-யையும் தவறாக மதிப்பிடலாம். தற்போதைய அல்லது வெளிப்புற தகவல்களுக்கு trusted retrieval sources சேர்க்கவும். High-stakes முடிவுகளுக்கு நிபுணர் சரிபார்ப்பு அவசியம்.
