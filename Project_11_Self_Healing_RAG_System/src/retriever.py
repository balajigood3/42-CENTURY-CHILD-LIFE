import re
from collections import Counter
from math import log

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_]+|[஀-௿]+",text.lower())

def split_chunks(text,chunk_words=180,overlap=30):
    words=text.split()
    if not words: return []
    chunks=[]; start=0
    while start<len(words):
        end=min(len(words),start+chunk_words)
        chunks.append(" ".join(words[start:end]))
        if end==len(words): break
        start=max(start+1,end-overlap)
    return chunks

class LocalRetriever:
    def __init__(self,chunk_words=180,overlap=30):
        self.chunk_words=chunk_words; self.overlap=overlap

    def index(self,documents):
        records=[]
        for name,text in documents.items():
            for i,chunk in enumerate(split_chunks(text,self.chunk_words,self.overlap)):
                records.append({"source":name,"chunk_id":i,"text":chunk})
        self.records=records
        return records

    def search(self,query,top_k=3):
        q=set(tokenize(query))
        scored=[]
        for rec in getattr(self,"records",[]):
            terms=tokenize(rec["text"]); counts=Counter(terms)
            if not terms: continue
            overlap=sum(counts[t] for t in q)
            # normalized lexical overlap; lightweight fallback retriever, not semantic embeddings
            score=overlap/(len(q)**0.5 * len(terms)**0.5) if q else 0.0
            scored.append((score,rec))
        scored.sort(key=lambda x:x[0],reverse=True)
        return [{"score":round(s,4),**r} for s,r in scored[:top_k]]
