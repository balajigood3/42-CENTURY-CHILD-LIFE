import requests

class AdaptiveAssistant:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",timeout=150):
        self.model=model
        self.base_url=base_url.rstrip("/")
        self.timeout=timeout

    def build_prompt(self,question,prefs):
        tone=prefs.get("tone","Clear and professional")
        detail=prefs.get("detail","Balanced")
        language=prefs.get("language","Tamil")
        detail_rule={"Short":"Answer briefly with essential points.",
                     "Balanced":"Give a useful explanation and examples when helpful.",
                     "Detailed":"Give a structured, thorough explanation with steps and examples."}.get(detail,"Give a balanced answer.")
        lang_rule={"Tamil":"Respond in natural Tamil; retain technical terms in English when clearer.",
                   "English":"Respond in English.",
                   "Tamil + English":"Explain in Tamil while retaining important English technical terms."}.get(language,"Respond in Tamil.")
        return f"""You are a reliable assistant. Adapt your answer to these explicit preferences.
Tone: {tone}
Detail: {detail_rule}
Language: {lang_rule}
Do not invent facts. State uncertainty when needed.
User request: {question}"""

    def respond(self,question,prefs):
        try:
            r=requests.post(f"{self.base_url}/api/generate",
                json={"model":self.model,"prompt":self.build_prompt(question,prefs),"stream":False,
                      "options":{"temperature":0.4}},timeout=self.timeout)
            r.raise_for_status()
            answer=r.json().get("response","").strip()
            return answer or "மாதிரியிலிருந்து காலியான பதில் கிடைத்தது."
        except requests.RequestException as exc:
            return f"Ollama-ஐ அணுக முடியவில்லை. `ollama serve` இயங்குகிறதா எனச் சரிபார்க்கவும். விவரம்: {exc}"
