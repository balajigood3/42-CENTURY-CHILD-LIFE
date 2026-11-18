import io, re
from collections import Counter
import fitz
import requests

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_]+|[஀-௿]+",text.lower())

class IntelligentPDFEngine:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",top_k=4,timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/"); self.top_k=top_k; self.timeout=timeout

    @staticmethod
    def extract_pdf(pdf_bytes):
        doc=fitz.open(stream=pdf_bytes,filetype="pdf")
        pages=[]
        for i,page in enumerate(doc):
            text=page.get_text("text").strip()
            pages.append({"page":i+1,"text":text})
        full="\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages if p["text"])
        metadata=doc.metadata or {}
        result={"text":full,"pages":pages,"page_count":len(doc),
                "metadata":{k:str(v) for k,v in metadata.items() if v}}
        doc.close()
        return result

    def retrieve(self,question,documents):
        q=set(tokenize(question)); hits=[]
        for name,data in documents.items():
            for page in data["pages"]:
                text=page["text"]
                if not text.strip(): continue
                terms=tokenize(text); counts=Counter(terms)
                score=sum(counts[t] for t in q)/(len(q)**0.5*len(terms)**0.5) if q and terms else 0
                if score>0:
                    hits.append({"source":name,"page":page["page"],"text":text[:7000],"score":round(score,4)})
        return sorted(hits,key=lambda x:x["score"],reverse=True)[:self.top_k]

    def ask(self,question,documents):
        hits=self.retrieve(question,documents)
        if not hits:
            return {"answer":"PDF-களில் கேள்விக்குப் பொருத்தமான text கிடைக்கவில்லை. PDF scanned/image-only ஆக இருக்கலாம் அல்லது கேள்வியை மாற்ற வேண்டியிருக்கலாம்.",
                    "status":"INSUFFICIENT_TEXT_MATCH","sources":[]}
        context="\n\n".join(f"[SOURCE: {h['source']} | PAGE: {h['page']}]\n{h['text']}" for h in hits)
        prompt=f"""Answer the question using only the PDF page excerpts below.
Cite each factual claim with the exact filename and page number in this format [filename, p. N].
If evidence is insufficient, say so. Do not invent page references or facts.
QUESTION: {question}
PDF EXCERPTS:
{context}
ANSWER:"""
        try:
            r=requests.post(f"{self.base_url}/api/generate",
                json={"model":self.model,"prompt":prompt,"stream":False,"options":{"temperature":0.1}},timeout=self.timeout)
            r.raise_for_status()
            answer=r.json().get("response","").strip() or "Model returned an empty response."
            status="ANSWERED_WITH_PAGE_CONTEXT"
        except requests.RequestException as exc:
            answer=f"Ollama connection error: {exc}"; status="MODEL_ERROR"
        return {"answer":answer,"status":status,"sources":hits}
