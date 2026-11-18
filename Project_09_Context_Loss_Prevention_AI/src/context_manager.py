import requests

class ContextManager:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",max_chars=1800,timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/")
        self.max_chars=max_chars; self.timeout=timeout

    def _generate(self,prompt,temperature=0.2):
        r=requests.post(f"{self.base_url}/api/generate",
            json={"model":self.model,"prompt":prompt,"stream":False,
                  "options":{"temperature":temperature}},timeout=self.timeout)
        r.raise_for_status()
        out=r.json().get("response","").strip()
        if not out: raise RuntimeError("Empty model response")
        return out

    def add_text(self,chunks,text):
        # Split long messages to keep each stored unit bounded.
        pieces=[text[i:i+self.max_chars] for i in range(0,len(text),self.max_chars)] or [text]
        updated=list(chunks)
        for piece in pieces:
            updated.append(piece)
        return updated[-40:]

    def build_memory(self,chunks,previous_memory=""):
        recent="\n\n".join(chunks[-12:])
        prompt=f"""Maintain a compact conversation memory for future question answering.
Preserve names, decisions, dates, requirements, constraints, unresolved questions, and important technical details.
Separate confirmed facts from assumptions. Do not invent missing details.
Previous memory:
{previous_memory}
New conversation excerpts:
{recent}
Return an updated concise memory."""
        return self._generate(prompt)

    def answer(self,question,memory,chunks):
        evidence="\n\n".join(chunks[-8:])
        prompt=f"""Answer the user's latest question using the conversation memory and excerpts.
Do not pretend to remember details that are absent. If context is insufficient, say what is missing.
MEMORY:
{memory}
RECENT EXCERPTS:
{evidence}
QUESTION:
{question}
ANSWER:"""
        try:
            return self._generate(prompt,temperature=0.3)
        except requests.RequestException as exc:
            return f"Ollama-ஐ அணுக முடியவில்லை: {exc}"
