# Project 4 – AI Contradiction Detection System

## தமிழ் விளக்கம்
இரண்டு உரைகள் அல்லது ஆவணங்களில் ஒரே தலைப்பு, காலம், அளவீடு மற்றும் சூழலில் ஒன்றுக்கொன்று பொருந்தாத கூற்றுகளை கண்டறியும் Generative AI பயன்பாடு.

## Detection labels
- `CONTRADICTION`: ஒரே scope-இல் நேரடி முரண்பாடு.
- `CONSISTENT`: கூற்றுகள் பொருந்துகின்றன.
- `DIFFERENT_SCOPE`: காலம், நிபந்தனை அல்லது வரம்பு வேறுபடுகிறது.
- `UNCLEAR`: கிடைத்த தகவலால் முடிவு செய்ய முடியவில்லை.

## Requirements
Python 3.10+, Ollama, local model இயங்குவதற்கான RAM/CPU/GPU. Paid API key தேவையில்லை.

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
Ollama service இயங்குவதை உறுதிசெய்து இரண்டு ஆதார உரைகளையும் உள்ளிடவும்.

## Tests
```bash
pytest -q
```

## Docker
Ollama host machine-ல் இயங்க வேண்டும். Container-ல் அணுகக்கூடிய URL அமைக்கவும்:
```bash
docker build -t contradiction-detector .
docker run --rm -p 8501:8501 -e OLLAMA_URL=http://host.docker.internal:11434/api/generate contradiction-detector
```
Linux-ல் தேவைக்கேற்ப `--add-host=host.docker.internal:host-gateway` சேர்க்கவும்.

## Limitations
LLM ஒப்பீடு தவறாக இருக்கலாம்; முக்கியமான முரண்பாடுகளை மனிதர் சரிபார்க்க வேண்டும். வெவ்வேறு காலம் அல்லது சூழலில் கூறப்பட்டவை முரண்பாடாக இருக்க வேண்டியதில்லை. இது சட்ட/அறிவியல் fact-checking சான்றிதழ் அல்ல.
