import json,requests
from config import OLLAMA_URL,MODEL_NAME,REQUEST_TIMEOUT
def ask_json(prompt):
    r=requests.post(OLLAMA_URL,json={"model":MODEL_NAME,"prompt":prompt,"stream":False,"format":"json","options":{"temperature":0.1}},timeout=REQUEST_TIMEOUT)
    r.raise_for_status(); raw=r.json().get("response","").strip()
    if not raw: raise ValueError("Local LLM வெற்று பதிலைத் தந்தது.")
    try: data=json.loads(raw)
    except json.JSONDecodeError as e: raise ValueError(f"LLM சரியான JSON தரவில்லை: {raw[:400]}") from e
    if not isinstance(data,dict): raise ValueError("LLM JSON object வழங்கவில்லை.")
    return data
