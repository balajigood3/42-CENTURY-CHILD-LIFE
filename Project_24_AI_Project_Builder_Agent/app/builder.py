from pathlib import Path
import json
import re
import os
import requests

class BuilderError(Exception):
    pass

ALLOWED_FILES = {
    "README.md", "requirements.txt", "main.py",
    "tests/test_app.py", "Dockerfile", "docker-compose.yml"
}
DEFAULT_TEMPLATES = {
    "README.md": "# {name}\n\n## Overview\n{description}\n\n## Run\n```bash\npip install -r requirements.txt\npython main.py\n```\n",
    "requirements.txt": "# Add Python dependencies here\n",
    "main.py": '"""Generated starter application."""\n\n\ndef main():\n    print("Hello from {name}")\n\n\nif __name__ == "__main__":\n    main()\n',
    "tests/test_app.py": "def test_generated_project_has_entrypoint():\n    from pathlib import Path\n    assert Path('main.py').exists()\n",
    "Dockerfile": """FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nCMD [\\"python\\", \\"main.py\\"]\n""",
    "docker-compose.yml": "services:\n  app:\n    build: .\n    restart: unless-stopped\n"
}

def slugify(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_").lower()
    if not value:
        raise BuilderError("Project name must contain letters or numbers.")
    return value[:48]

def _ollama_generate(spec: dict, timeout: int = 90) -> dict | None:
    prompt = f"""Create a small, safe Python starter project as JSON.
Project specification: {json.dumps(spec, ensure_ascii=False)}
Return ONLY a JSON object with keys README.md, requirements.txt, main.py,
tests/test_app.py, Dockerfile, docker-compose.yml.
Each value must be plain file content as a string.
Constraints: no paid APIs, no secrets, no shell execution, no network listener,
no destructive file operations, standard library preferred, include runnable main.py.
"""
    try:
        response = requests.post(
            os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/generate",
            json={"model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
                  "prompt": prompt, "stream": False, "format": "json"},
            timeout=timeout
        )
        response.raise_for_status()
        data = json.loads(response.json().get("response", "{}"))
        return data if isinstance(data, dict) else None
    except (requests.RequestException, ValueError, json.JSONDecodeError):
        return None

def build_project(name: str, description: str, output_root="generated_projects",
                  use_llm=True) -> dict:
    if not description.strip():
        raise BuilderError("Project description cannot be empty.")
    slug = slugify(name)
    spec = {"name": name.strip(), "description": description.strip()}
    generated = _ollama_generate(spec) if use_llm else None
    used_llm = bool(generated)
    contents = {}
    for filename in ALLOWED_FILES:
        raw = generated.get(filename) if generated else None
        if not isinstance(raw, str) or not raw.strip():
            raw = DEFAULT_TEMPLATES[filename].format(name=name.strip(), description=description.strip())
        contents[filename] = raw

    root = Path(output_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = (root / slug).resolve()
    if root not in target.parents:
        raise BuilderError("Invalid project output path.")
    if target.exists():
        raise BuilderError("A project with this name already exists. Choose another name.")
    target.mkdir(parents=True)
    for filename, content in contents.items():
        path = target / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    manifest = {
        "project_name": name.strip(),
        "slug": slug,
        "description": description.strip(),
        "generator": "ollama" if used_llm else "safe_template_fallback",
        "files": sorted(contents.keys())
    }
    (target / "project_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"path": str(target), "manifest": manifest}
