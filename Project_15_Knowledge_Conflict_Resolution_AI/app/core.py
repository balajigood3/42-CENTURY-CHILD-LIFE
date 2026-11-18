from __future__ import annotations
import json, re
from dataclasses import dataclass
from typing import Any

def parse_json_response(text: str) -> Any:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try: return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}|\[.*\]", text, flags=re.S)
        if not m: raise ValueError("Model did not return valid JSON")
        return json.loads(m.group(0))

def tokenize(text):
    stop={"the","and","for","with","from","that","this","are","was"}
    return {w.lower() for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9._%-]*",text)
            if len(w)>2 and w.lower() not in stop}

def lexical_similarity(a,b):
    x,y=tokenize(a),tokenize(b)
    return len(x&y)/max(1,len(x|y))

def heuristic_candidates(claims,threshold=.12):
    out=[]
    for i,a in enumerate(claims):
        for b in claims[i+1:]:
            if a.get("source_id")==b.get("source_id"): continue
            score=lexical_similarity(a.get("claim",""),b.get("claim",""))
            shared=tokenize(a.get("claim",""))&tokenize(b.get("claim",""))
            numeric=bool(re.search(r"\d",a.get("claim","")) or re.search(r"\d",b.get("claim","")))
            if score>=threshold or (len(shared)>=2 and numeric): out.append((a,b,round(score,3)))
    return out

@dataclass
class Conflict:
    claim_a:str; source_a:str; claim_b:str; source_b:str
    classification:str; severity:str; explanation:str; resolution:str
    confidence:float; evidence_needed:str=""

class OllamaClient:
    def __init__(self,model="qwen2.5:3b",host="http://localhost:11434"):
        self.model,self.host=model,host.rstrip("/")
    def generate(self,prompt):
        import urllib.request
        body=json.dumps({"model":self.model,"prompt":prompt,"stream":False,
                         "options":{"temperature":.1}}).encode()
        req=urllib.request.Request(self.host+"/api/generate",data=body,
             headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                return json.loads(r.read().decode())["response"]
        except Exception as e: raise RuntimeError(f"Ollama request failed: {e}") from e

def extract_claims(text,source_id,client):
    prompt=("Extract up to 20 factual claims. Preserve exact values, dates, units and qualifiers. "
      'Return ONLY a JSON array. Each item: {"claim":"...","topic":"...","time_scope":"...","entity":"..."}. '
      f"Source: {source_id}\nDOCUMENT:\n{text[:14000]}")
    data=parse_json_response(client.generate(prompt))
    if not isinstance(data,list): raise ValueError("Expected a JSON array of claims")
    return [{"claim":str(x["claim"]),"topic":str(x.get("topic","")),
       "time_scope":str(x.get("time_scope","")),"entity":str(x.get("entity","")),
       "source_id":source_id} for x in data if isinstance(x,dict) and x.get("claim")]

def compare_claims(a,b,client):
    prompt=("Compare two claims without assuming either is true. Classify as "
      "DIRECT_CONTRADICTION, SCOPE_OR_TIME_DIFFERENCE, COMPATIBLE, or INSUFFICIENT_INFORMATION. "
      'Return ONLY JSON keys: classification, severity (low/medium/high), explanation, resolution, '
      "confidence (0..1), evidence_needed. Do not invent facts; state what evidence is needed.\n"
      f"A [{a['source_id']}]: {a['claim']}\nB [{b['source_id']}]: {b['claim']}")
    d=parse_json_response(client.generate(prompt))
    allowed={"DIRECT_CONTRADICTION","SCOPE_OR_TIME_DIFFERENCE","COMPATIBLE","INSUFFICIENT_INFORMATION"}
    cls=str(d.get("classification","INSUFFICIENT_INFORMATION")).upper()
    if cls not in allowed: cls="INSUFFICIENT_INFORMATION"
    try: conf=max(0.,min(1.,float(d.get("confidence",0))))
    except (ValueError,TypeError): conf=0.
    return Conflict(a["claim"],a["source_id"],b["claim"],b["source_id"],cls,
      str(d.get("severity","low")).lower(),str(d.get("explanation","")),
      str(d.get("resolution","")),conf,str(d.get("evidence_needed","")))

def analyze_documents(documents,client,threshold=.12):
    claims=[]
    for source,body in documents.items(): claims.extend(extract_claims(body,source,client))
    return claims,[compare_claims(a,b,client) for a,b,_ in heuristic_candidates(claims,threshold)]

def report_markdown(claims,conflicts):
    lines=["# Knowledge Conflict Analysis","",f"- Extracted claims: {len(claims)}",
      f"- Candidate pairs reviewed: {len(conflicts)}","",
      "> This report identifies possible inconsistencies; it does not establish truth.",""]
    if not conflicts: lines.append("No candidate conflict pairs were found by the lexical pre-filter.")
    for i,c in enumerate(conflicts,1):
      lines += [f"## Finding {i}: {c.classification}","",
        f"**Severity:** {c.severity} | **Confidence:** {c.confidence:.2f}","",
        f"**Source {c.source_a}:** {c.claim_a}","",f"**Source {c.source_b}:** {c.claim_b}","",
        f"**Explanation:** {c.explanation}","",f"**Suggested resolution:** {c.resolution}","",
        f"**Evidence needed:** {c.evidence_needed}",""]
    return "\n".join(lines)
