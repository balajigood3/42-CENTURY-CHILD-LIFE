import json, re, hashlib
from datetime import datetime, timezone

def parse_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if not match:
            raise ValueError("Invalid JSON returned by model")
        return json.loads(match.group(0))

class OllamaClient:
    def __init__(self, model="qwen2.5:3b", host="http://localhost:11434"):
        self.model, self.host = model, host.rstrip("/")
    def generate(self, prompt):
        import urllib.request
        body = json.dumps({"model":self.model,"prompt":prompt,"stream":False,
                           "options":{"temperature":0.1}}).encode()
        req = urllib.request.Request(self.host+"/api/generate",data=body,
                                     headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                return json.loads(r.read().decode())["response"]
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def extract_memories(text, client, source="user_input"):
    prompt = (
      "Extract durable, useful facts and preferences explicitly stated in this text. "
      "Do not infer sensitive personal attributes, passwords, secrets, or uncertain details. "
      "Return ONLY JSON array of objects with keys: memory (short standalone statement), "
      "category, importance (1-5), confidence (0-1), expires (true/false). "
      "Skip temporary one-time details. Preserve the user's wording and do not invent facts.\n"
      f"TEXT:\n{text[:10000]}"
    )
    data = parse_json(client.generate(prompt))
    if not isinstance(data,list):
        raise ValueError("Expected a JSON array")
    memories=[]
    for item in data:
        if not isinstance(item,dict) or not item.get("memory"): continue
        try: importance=max(1,min(5,int(item.get("importance",3))))
        except (ValueError,TypeError): importance=3
        try: confidence=max(0.,min(1.,float(item.get("confidence",0))))
        except (ValueError,TypeError): confidence=0.
        memories.append({
          "memory":str(item["memory"]).strip(),
          "category":str(item.get("category","general")).strip()[:60],
          "importance":importance,"confidence":confidence,
          "expires":bool(item.get("expires",False)),"source":source
        })
    return memories

def retrieve_memories(query, memories, limit=8):
    terms=set(re.findall(r"[a-z0-9]+",query.lower()))
    scored=[]
    for item in memories:
        text=(item["memory"]+" "+item.get("category","")).lower()
        words=set(re.findall(r"[a-z0-9]+",text))
        overlap=len(terms & words)/max(1,len(terms))
        if overlap:
            score=overlap*(0.7+0.06*item.get("importance",3))
            scored.append((score,item))
    scored.sort(key=lambda x:x[0],reverse=True)
    return [item for _,item in scored[:limit]]

def answer_with_memory(query, memories, client):
    selected=retrieve_memories(query,memories)
    context="\n".join(f"- {m['memory']} (source: {m.get('source','unknown')})" for m in selected)
    prompt=("Answer the user's query. Use the memory context only when relevant. "
      "Do not treat a memory as guaranteed current or complete. If context is missing, "
      "ask the user rather than guessing. Do not reveal unrelated stored memories.\n"
      f"MEMORY CONTEXT:\n{context or '[No relevant memories retrieved]'}\n"
      f"QUERY:\n{query}")
    return client.generate(prompt),selected

def normalize_memory(text):
    return re.sub(r"\s+"," ",text.strip()).casefold()
