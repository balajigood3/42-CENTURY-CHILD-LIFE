import re
from dataclasses import dataclass
ALLOWED={"str","int","float","bool"}
@dataclass(frozen=True)
class Field: name:str; kind:str
@dataclass(frozen=True)
class Spec: name:str; slug:str; entity:str; fields:tuple
def slugify(v):
 if "/" in v or chr(92) in v or ".." in v: raise ValueError("Path characters are not allowed in project names")
 s=re.sub(r"[^a-z0-9]+","-",v.strip().lower()).strip("-")
 if not s: raise ValueError("Project name must contain letters or numbers")
 return s[:48]
def ident(v,label):
 if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}",v.strip()): raise ValueError(label+" must be a valid identifier")
 return v.strip()
def parse_spec(name,entity,raw):
 if not name.strip(): raise ValueError("Application name required")
 seen=set(); fields=[]
 for part in raw.split(","):
  if not part.strip(): continue
  if ":" not in part: raise ValueError("Use field:type syntax")
  n,k=[x.strip() for x in part.split(":",1)]; n=ident(n,"Field")
  if n in seen or n in {"id","created_at"}: raise ValueError("Duplicate or reserved field: "+n)
  if k not in ALLOWED: raise ValueError("Unsupported type: "+k)
  seen.add(n); fields.append(Field(n,k))
 if not fields: raise ValueError("At least one field required")
 if len(fields)>12: raise ValueError("Maximum 12 fields")
 return Spec(name.strip(),slugify(name),ident(entity,"Entity"),tuple(fields))
