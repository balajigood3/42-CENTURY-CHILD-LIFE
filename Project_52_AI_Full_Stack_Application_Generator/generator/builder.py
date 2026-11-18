import io,json
from zipfile import ZipFile,ZIP_DEFLATED
PY={"str":"str","int":"int","float":"float","bool":"bool"}
SQL={"str":"TEXT","int":"INTEGER","float":"REAL","bool":"INTEGER"}
TS={"str":"string","int":"number","float":"number","bool":"boolean"}
def build_project(s):
 e=s.entity; t=e.lower(); fs=s.fields
 pf="\\n".join("    %s: %s"%(f.name,PY[f.kind]) for f in fs)
 sc=", ".join('"%s" %s'%(f.name,SQL[f.kind]) for f in fs)
 cols=", ".join('"%s"'%f.name for f in fs); marks=", ".join("?" for f in fs)
 vals=", ".join("item.%s"%f.name for f in fs)
 tf="\\n".join("  %s: %s;"%(f.name,TS[f.kind]) for f in fs)
 defaults=", ".join("%s: %s"%(f.name,"false" if f.kind=="bool" else "0" if f.kind in ("int","float") else '""') for f in fs)
 controls="\\n".join('<label>%s<input name="%s" type="%s" /></label>'%(f.name,f.name,"checkbox" if f.kind=="bool" else "number" if f.kind in ("int","float") else "text") for f in fs)
 backend = (
  "from fastapi import FastAPI,HTTPException\\nfrom fastapi.middleware.cors import CORSMiddleware\\nfrom pydantic import BaseModel\\nimport sqlite3\\nfrom pathlib import Path\\n"
  "DB=Path(__file__).with_name('app.db')\\napp=FastAPI(title="+repr(s.name+" API")+")\\n"
  "app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['*'],allow_headers=['*'])\\n"
  "class %sCreate(BaseModel):\\n%s\\n"%(e,pf)+
  "def db():\\n c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c\\n"
  "@app.on_event('startup')\\ndef init():\\n with db() as c: c.execute(%r)\\n"%("CREATE TABLE IF NOT EXISTS %s (id INTEGER PRIMARY KEY AUTOINCREMENT, %s)"%(t,sc))+
  "@app.get('/health')\\ndef health(): return {'status':'ok'}\\n"
  "@app.get('/%s')\\ndef list_items():\\n with db() as c: return [dict(r) for r in c.execute('SELECT * FROM %s ORDER BY id DESC')]\\n"%(t,t)+
  "@app.post('/%s',status_code=201)\\ndef create_item(item:%sCreate):\\n with db() as c:\\n  cur=c.execute('INSERT INTO %s (%s) VALUES (%s)',(%s,))\\n  return dict(c.execute('SELECT * FROM %s WHERE id=?',(cur.lastrowid,)).fetchone())\\n"%(t,e,t,cols,marks,vals,t)+
  "@app.delete('/%s/{item_id}',status_code=204)\\ndef delete_item(item_id:int):\\n with db() as c:\\n  cur=c.execute('DELETE FROM %s WHERE id=?',(item_id,))\\n  if cur.rowcount==0: raise HTTPException(404,'Record not found')\\n"%(t,t)
 )
 frontend = (
  'import {useEffect,useState,type FormEvent} from "react";\\nimport type {RecordInput,RecordItem} from "./types";\\nconst API=import.meta.env.VITE_API_URL||"http://localhost:8000";\\nconst empty:RecordInput={%s};\\n'%defaults+
  'export default function App(){const [items,setItems]=useState<RecordItem[]>([]);const [form,setForm]=useState<RecordInput>(empty);const [error,setError]=useState("");\\n'
  'async function refresh(){const r=await fetch(`${API}/%s`);if(!r.ok)throw Error("Load failed");setItems(await r.json());}\\n'%t+
  'useEffect(()=>{refresh().catch(e=>setError(e.message));},[]);\\n'
  'async function submit(e:FormEvent){e.preventDefault();setError("");try{const r=await fetch(`${API}/%s`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});if(!r.ok)throw Error("Save failed");setForm(empty);await refresh();}catch(e){setError(e instanceof Error?e.message:"Unexpected error");}}\\n'%t+
  'async function remove(id:number){const r=await fetch(`${API}/%s/${id}`,{method:"DELETE"});if(!r.ok){setError("Delete failed");return;}await refresh();}\\n'%t+
  'return <main><h1>%s</h1><form onSubmit={submit}>\\n%s\\n<button>Save</button></form>{error&&<p role="alert">{error}</p>}<h2>%s records</h2>{items.map(x=><article key={x.id}><pre>{JSON.stringify(x,null,2)}</pre><button onClick={()=>remove(x.id)}>Delete</button></article>)}</main>}\\n'%(s.name,controls,e)
 )
 readme="# %s\\n\\nReact + TypeScript frontend, FastAPI backend, SQLite persistence.\\n\\nBackend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`\\n\\nFrontend: `cd frontend && npm install && npm run dev`\\n\\nAPI docs: http://localhost:8000/docs\\n\\nDocker: `docker compose up --build`\\n\\nThis is a starter scaffold, not production-ready. Add authentication, authorization, migrations, secrets management, stronger validation, logging, and deployment hardening before real use."%s.name
 return {
 "README.md":readme,
 "backend/main.py":backend,
 "backend/requirements.txt":"fastapi>=0.110,<1\\nuvicorn[standard]>=0.27,<1\\npydantic>=2,<3\\n",
 "backend/Dockerfile":'FROM python:3.11-slim\\nWORKDIR /app\\nCOPY requirements.txt .\\nRUN pip install --no-cache-dir -r requirements.txt\\nCOPY . .\\nEXPOSE 8000\\nCMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]\\n',
 "frontend/package.json":json.dumps({"name":s.slug+"-ui","version":"0.1.0","private":True,"type":"module","scripts":{"dev":"vite --host 0.0.0.0","build":"tsc && vite build"},"dependencies":{"react":"latest","react-dom":"latest","vite":"latest","@vitejs/plugin-react":"latest"},"devDependencies":{"typescript":"latest"}},indent=2),
 "frontend/index.html":'<div id="root"></div><script type="module" src="/src/main.tsx"></script>',
 "frontend/tsconfig.json":json.dumps({"compilerOptions":{"target":"ES2020","module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":True,"skipLibCheck":True,"noEmit":True,"lib":["ES2020","DOM"]},"include":["src"]},indent=2),
 "frontend/vite.config.ts":'import {defineConfig} from "vite";import react from "@vitejs/plugin-react";export default defineConfig({plugins:[react()]});',
 "frontend/src/main.tsx":'import React from "react";import {createRoot} from "react-dom/client";import App from "./App";import "./style.css";createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);',
 "frontend/src/types.ts":"export type RecordInput={\\n%s\\n};\\nexport type RecordItem=RecordInput&{id:number};"%tf,
 "frontend/src/App.tsx":frontend,
 "frontend/src/style.css":'body{font-family:system-ui;margin:0;background:#f3f5f7;color:#18212b}main{max-width:850px;margin:3rem auto;padding:1rem}form,article{background:white;padding:1rem;margin:1rem 0;border-radius:10px;display:grid;gap:.8rem}label{display:grid;gap:.3rem}input,button{padding:.65rem;border:1px solid #ccd2d8;border-radius:6px}button{background:#183b56;color:white;cursor:pointer}pre{white-space:pre-wrap}',
 "frontend/Dockerfile":'FROM node:20-alpine\\nWORKDIR /app\\nCOPY package.json .\\nRUN npm install\\nCOPY . .\\nEXPOSE 5173\\nCMD ["npm","run","dev","--","--host","0.0.0.0"]\\n',
 "docker-compose.yml":'services:\\n  api:\\n    build: ./backend\\n    ports: ["8000:8000"]\\n  web:\\n    build: ./frontend\\n    ports: ["5173:5173"]\\n    depends_on: [api]\\n',
 "Dockerfile":'FROM python:3.11-slim\\nWORKDIR /app\\nCOPY requirements.txt .\\nRUN pip install --no-cache-dir -r requirements.txt\\nCOPY . .\\nEXPOSE 8501\\nCMD ["streamlit","run","app.py","--server.address=0.0.0.0"]\\n',
 "docker-compose.generator.yml":'services:\\n  generator:\\n    build: .\\n    ports: ["8501:8501"]\\n',
 "requirements.txt":"streamlit>=1.32,<2\\n",
 ".env.example":"VITE_API_URL=http://localhost:8000\\n",
 ".dockerignore":"__pycache__\\n.pytest_cache\\n.venv\\n.git\\n"
 }
def make_zip(files):
 b=io.BytesIO()
 with ZipFile(b,"w",ZIP_DEFLATED) as z:
  for n,v in sorted(files.items()): z.writestr(n,v)
 return b.getvalue()
