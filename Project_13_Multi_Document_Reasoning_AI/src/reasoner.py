import re
import requests
from collections import Counter

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_]+|[஀-௿]+",text.lower())

def chunks(text,size=160,overlap=25):
    words=text.split(); out=[]; start=0
    while start<len(words):
        end=min(len(words),start+size); out.append(" ".join(words[start:end]))
        if end==len(words): break
        start=max(start+1,end-overlap)
    return out

class MultiDocumentReasoner:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",top_k=2,timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/"); self.top_k=top_k; self.timeout=timeout

    def retrieve(self,question,documents):
        q=set(tokenize(question)); evidence={}; coverage={}
        for name,text in documents.items():
            scored=[]
            for idx,part in enumerate(chunks(text)):
                terms=tokenize(part); counts=Counter(terms)
                score=sum(counts[t] for t in q)/(len(q)**0.5*len(terms)**0.5) if q and terms else 0
                scored.append({"chunk":idx,"text":part,"score":round(score,4)})
            scored.sort(key=lambda x:x["score"],reverse=True)
            selected=[x for x in scored[:self.top_k] if x["score"]>0]
            evidence[name]=selected
            coverage[name]={"retrieved_passages":len(selected),"total_chunks":len(scored),
                            "best_score":scored[0]["score"] if scored else 0}
        return evidence,coverage

    def reason(self,question,documents):
        evidence,coverage=self.retrieve(question,documents)
        usable={k:v for k,v in evidence.items() if v}
        if not usable:
            return {"answer":"கேள்விக்குப் பொருத்தமான தகவல் எந்த ஆவணத்திலும் கிடைக்கவில்லை. கேள்வியை மாற்றவும் அல்லது தொடர்புடைய ஆவணங்களைச் சேர்க்கவும்.",
                    "evidence":evidence,"coverage":coverage}
        context=[]
        for name,passages in usable.items():
            for p in passages:
                context.append(f"[DOCUMENT: {name} | CHUNK: {p['chunk']}] {p['text']}")
        prompt=f"""You are a careful multi-document analysis assistant.
Answer the user's task by comparing and synthesizing the supplied passages.
Separate agreement, disagreement, unique information, and missing evidence when relevant.
Cite document filenames next to claims. Do not invent facts or assume the retrieved excerpts represent the entire documents.
If evidence conflicts, report the conflict instead of choosing arbitrarily.
QUESTION: {question}
PASSAGES:
{chr(10).join(context)}
STRUCTURED ANSWER:"""
        try:
            r=requests.post(f"{self.base_url}/api/generate",
                json={"model":self.model,"prompt":prompt,"stream":False,"options":{"temperature":0.1}},timeout=self.timeout)
            r.raise_for_status(); answer=r.json().get("response","").strip() or "Model returned an empty response."
        except requests.RequestException as exc:
            answer=f"Ollama connection error: {exc}"
        return {"answer":answer,"evidence":evidence,"coverage":coverage}
