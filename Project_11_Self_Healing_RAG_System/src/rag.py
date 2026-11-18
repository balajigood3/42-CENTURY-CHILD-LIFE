import requests
from src.retriever import LocalRetriever

class SelfHealingRAG:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",top_k=3,threshold=0.12,timeout=180):
        self.model=model; self.base_url=base_url.rstrip("/")
        self.top_k=top_k; self.threshold=threshold; self.timeout=timeout
        self.retriever=LocalRetriever()

    def _generate(self,prompt,temperature=0.1):
        r=requests.post(f"{self.base_url}/api/generate",
            json={"model":self.model,"prompt":prompt,"stream":False,
                  "options":{"temperature":temperature}},timeout=self.timeout)
        r.raise_for_status()
        text=r.json().get("response","").strip()
        if not text: raise RuntimeError("Empty Ollama response")
        return text

    def _retrieve(self,query):
        return self.retriever.search(query,self.top_k)

    def ask(self,question,documents):
        self.retriever.index(documents)
        hits=self._retrieve(question)
        attempts=[{"query":question,"top_scores":[h["score"] for h in hits]}]
        # Repair 1: rewrite query if lexical retrieval is weak.
        if not hits or hits[0]["score"] < self.threshold:
            try:
                rewritten=self._generate(
                    "Rewrite this question into 3 concise keyword-rich search queries. "
                    "Return only the queries, one per line. Do not answer it.\nQuestion: "+question)
                candidates=[line.strip("- •0123456789.\t") for line in rewritten.splitlines() if line.strip()]
                best=[]
                for candidate in candidates[:3]:
                    candidate_hits=self._retrieve(candidate)
                    attempts.append({"query":candidate,"top_scores":[h["score"] for h in candidate_hits]})
                    if candidate_hits and (not best or candidate_hits[0]["score"]>best[0]["score"]):
                        best=candidate_hits
                if best and (not hits or best[0]["score"]>hits[0]["score"]): hits=best
            except requests.RequestException:
                pass
        if not hits or hits[0]["score"] < self.threshold:
            return {"answer":"பதிவேற்றிய ஆவணங்களில் இந்தக் கேள்விக்குப் பொருத்தமான ஆதாரம் கிடைக்கவில்லை. ஆவணத்தைச் சேர்க்கவும் அல்லது கேள்வியை மாற்றவும்.",
                    "status":"INSUFFICIENT_CONTEXT","chunks":[],"diagnostics":{"attempts":attempts,"repair":"query rewrite attempted","threshold":self.threshold}}
        context="\n\n".join(f"[Source: {h['source']} | Chunk: {h['chunk_id']}] {h['text']}" for h in hits)
        prompt=f"""Answer using only the retrieved context. Cite source filenames in square brackets.
If the context does not contain the answer, say that evidence is insufficient. Do not use outside knowledge.
QUESTION: {question}
RETRIEVED CONTEXT:
{context}
ANSWER:"""
        try:
            answer=self._generate(prompt)
        except requests.RequestException as exc:
            answer=f"Ollama connection error: {exc}"
        return {"answer":answer,"status":"CONTEXT_RETRIEVED","chunks":[{"source":h["source"],"score":h["score"],"text":h["text"]} for h in hits],
                "diagnostics":{"attempts":attempts,"repair":"query rewrite if initial retrieval score was below threshold","threshold":self.threshold}}
