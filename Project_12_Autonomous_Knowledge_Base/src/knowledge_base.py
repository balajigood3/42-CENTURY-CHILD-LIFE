import sqlite3, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
import requests
from collections import Counter

DB=Path("data/knowledge.db")

def tokens(text):
    return re.findall(r"[a-zA-Z0-9_]+|[஀-௿]+",text.lower())

def chunk_text(text,size=180,overlap=30):
    words=text.split(); out=[]; start=0
    while start<len(words):
        end=min(len(words),start+size); out.append(" ".join(words[start:end]))
        if end==len(words): break
        start=max(start+1,end-overlap)
    return out

class AutonomousKnowledgeBase:
    def __init__(self,model="qwen2.5:3b",base_url="http://localhost:11434",db_path=DB):
        self.model=model; self.base_url=base_url.rstrip("/"); self.db_path=Path(db_path)
        self.db_path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS documents(
                id INTEGER PRIMARY KEY, name TEXT UNIQUE, digest TEXT, updated_at TEXT)""")
            c.execute("""CREATE TABLE IF NOT EXISTS chunks(
                id INTEGER PRIMARY KEY, document_id INTEGER, chunk_no INTEGER, content TEXT,
                FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE)""")

    def connect(self):
        c=sqlite3.connect(self.db_path); c.execute("PRAGMA foreign_keys=ON"); return c

    def ingest(self,uploads):
        added=0
        with self.connect() as c:
            for f in uploads:
                raw=f.getvalue().decode("utf-8",errors="replace")
                digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
                row=c.execute("SELECT id,digest FROM documents WHERE name=?",(f.name,)).fetchone()
                if row and row[1]==digest: continue
                if row:
                    doc_id=row[0]
                    c.execute("DELETE FROM chunks WHERE document_id=?",(doc_id,))
                    c.execute("UPDATE documents SET digest=?,updated_at=? WHERE id=?",
                              (digest,datetime.now(timezone.utc).isoformat(),doc_id))
                else:
                    cur=c.execute("INSERT INTO documents(name,digest,updated_at) VALUES(?,?,?)",
                                  (f.name,digest,datetime.now(timezone.utc).isoformat()))
                    doc_id=cur.lastrowid
                parts=chunk_text(raw)
                c.executemany("INSERT INTO chunks(document_id,chunk_no,content) VALUES(?,?,?)",
                              [(doc_id,i,p) for i,p in enumerate(parts)])
                added+=len(parts)
            total=c.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return {"added":added,"total":total}

    def list_documents(self):
        with self.connect() as c:
            rows=c.execute("""SELECT d.name,COUNT(ch.id),d.updated_at FROM documents d
                LEFT JOIN chunks ch ON ch.document_id=d.id GROUP BY d.id ORDER BY d.name""").fetchall()
        return [{"name":r[0],"chunks":r[1],"updated_at":r[2]} for r in rows]

    def search(self,query,top_k=4):
        q=set(tokens(query))
        with self.connect() as c:
            rows=c.execute("""SELECT d.name,ch.chunk_no,ch.content FROM chunks ch
                JOIN documents d ON d.id=ch.document_id""").fetchall()
        ranked=[]
        for name,no,content in rows:
            ts=tokens(content); counts=Counter(ts)
            score=sum(counts[t] for t in q)/(len(q)**0.5*len(ts)**0.5) if q and ts else 0
            ranked.append({"source":name,"chunk_no":no,"text":content,"score":round(score,4)})
        return sorted(ranked,key=lambda x:x["score"],reverse=True)[:top_k]

    def ask(self,question,top_k=4):
        hits=self.search(question,top_k)
        if not hits or hits[0]["score"]<=0:
            return {"answer":"இந்த knowledge base-ல் கேள்விக்குப் பொருத்தமான தகவல் கிடைக்கவில்லை. தொடர்புடைய ஆவணத்தை upload செய்யவும்.",
                    "status":"INSUFFICIENT_KNOWLEDGE","sources":[]}
        context="\n\n".join(f"[{h['source']} | chunk {h['chunk_no']}] {h['text']}" for h in hits)
        prompt=f"""Answer only from the knowledge base passages below.
Cite the source filename for factual claims. If the passages do not answer the question, state that knowledge is insufficient.
Do not invent details.
QUESTION: {question}
PASSAGES:
{context}
ANSWER:"""
        try:
            r=requests.post(f"{self.base_url}/api/generate",
                json={"model":self.model,"prompt":prompt,"stream":False,"options":{"temperature":0.1}},timeout=180)
            r.raise_for_status(); answer=r.json().get("response","").strip()
            if not answer: answer="Model returned an empty response."
            status="ANSWERED_FROM_KB"
        except requests.RequestException as e:
            answer=f"Ollama connection error: {e}"; status="MODEL_ERROR"
        return {"answer":answer,"status":status,"sources":hits}

    def clear(self):
        with self.connect() as c:
            c.execute("DELETE FROM chunks"); c.execute("DELETE FROM documents")
