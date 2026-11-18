from pathlib import Path
from datetime import datetime, timezone
import json

def save_generation(path, field, observation, result):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    record = {"created_at": datetime.now(timezone.utc).isoformat(),
              "field": field, "observation": observation, "result": result}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_generations(path, limit=20):
    file = Path(path)
    if not file.exists() or limit <= 0:
        return []
    rows = []
    for line in file.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]
