from __future__ import annotations
import json, keyword, zipfile
from pathlib import Path
from .schema import validate_spec

PY_TYPES = {"str": "str", "int": "int", "float": "float", "bool": "bool"}

def render_model(spec: dict) -> str:
    lines = ["from pydantic import BaseModel, ConfigDict", "", "", f"class {spec['name']}Create(BaseModel):",
             "    model_config = ConfigDict(extra='forbid')"]
    for field in spec["fields"]:
        annotation = PY_TYPES[field["type"]]
        default = "" if field["required"] else " = None"
        if not field["required"]:
            annotation += " | None"
        lines.append(f"    {field['name']}: {annotation}{default}")
    lines += ["", "", f"class {spec['name']}Update(BaseModel):",
              "    model_config = ConfigDict(extra='forbid')"]
    for field in spec["fields"]:
        lines.append(f"    {field['name']}: {PY_TYPES[field['type']]} | None = None")
    lines.append("")
    return "\n".join(lines)

def render_app(spec: dict) -> str:
    model = spec["name"]
    path = spec["endpoint"]
    methods = set(spec["methods"])
    lines = [
        "from fastapi import FastAPI, HTTPException, status",
        "from typing import Any",
        f"from models import {model}Create, {model}Update",
        "",
        f"app = FastAPI(title={json.dumps(model + ' API')}, version='1.0.0')",
        f"DB: dict[int, dict[str, Any]] = {{}}",
        "NEXT_ID = 1",
        "",
        "@app.get('/health')",
        "def health():",
        "    return {'status': 'ok'}",
        "",
    ]
    if "POST" in methods:
        lines += [f"@app.post({json.dumps(path)}, status_code=status.HTTP_201_CREATED)",
                  f"def create_{model.lower()}(payload: {model}Create):",
                  "    global NEXT_ID",
                  "    item = payload.model_dump()",
                  "    item['id'] = NEXT_ID",
                  "    DB[NEXT_ID] = item",
                  "    NEXT_ID += 1",
                  "    return item", ""]
    if "GET" in methods:
        lines += [f"@app.get({json.dumps(path)})",
                  f"def list_{model.lower()}s():",
                  "    return list(DB.values())", "",
                  f"@app.get({json.dumps(path + '/{item_id}')})",
                  f"def get_{model.lower()}(item_id: int):",
                  "    item = DB.get(item_id)",
                  "    if item is None:",
                  "        raise HTTPException(status_code=404, detail='Item not found')",
                  "    return item", ""]
    if "PUT" in methods:
        lines += [f"@app.put({json.dumps(path + '/{item_id}')})",
                  f"def replace_{model.lower()}(item_id: int, payload: {model}Create):",
                  "    if item_id not in DB:",
                  "        raise HTTPException(status_code=404, detail='Item not found')",
                  "    item = payload.model_dump()",
                  "    item['id'] = item_id",
                  "    DB[item_id] = item",
                  "    return item", ""]
    if "PATCH" in methods:
        lines += [f"@app.patch({json.dumps(path + '/{item_id}')})",
                  f"def update_{model.lower()}(item_id: int, payload: {model}Update):",
                  "    if item_id not in DB:",
                  "        raise HTTPException(status_code=404, detail='Item not found')",
                  "    changes = payload.model_dump(exclude_unset=True)",
                  "    DB[item_id].update(changes)",
                  "    return DB[item_id]", ""]
    if "DELETE" in methods:
        lines += [f"@app.delete({json.dumps(path + '/{item_id}')}, status_code=status.HTTP_204_NO_CONTENT)",
                  f"def delete_{model.lower()}(item_id: int):",
                  "    if item_id not in DB:",
                  "        raise HTTPException(status_code=404, detail='Item not found')",
                  "    del DB[item_id]",
                  "    return None", ""]
    return "\n".join(lines)

def generate_files(raw_spec: dict) -> dict[str, str]:
    spec = validate_spec(raw_spec)
    readme = f"""# Generated {spec['name']} API

## Quick start
```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://localhost:8000/docs for interactive OpenAPI documentation.

## API
- Resource: `{spec['endpoint']}`
- Generated methods: {", ".join(spec['methods'])}
- Storage: in-memory demo store (data resets on restart).

## Important
This is a starter scaffold. Add persistent storage, authentication, authorization,
rate limiting, logging, migrations, and production deployment controls before use.
"""
    return {
        "main.py": render_app(spec),
        "models.py": render_model(spec),
        "requirements.txt": """fastapi>=0.110,<1.0
uvicorn[standard]>=0.27,<1.0
pydantic>=2.6,<3.0
""",
        "README.md": readme,
        "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
""",
        "docker-compose.yml": """services:
  generated-api:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
""",
        ".dockerignore": """__pycache__/
.venv/
.pytest_cache/
.git/
""",
        "api-spec.json": json.dumps(spec, indent=2) + chr(10),
    }

def export_project(raw_spec: dict, output_zip: str | Path) -> Path:
    artifacts = generate_files(raw_spec)
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in artifacts.items():
            zf.writestr(name, content)
    return output_zip
