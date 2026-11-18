from pathlib import Path
from datetime import datetime, timezone
import json

def save_analysis(path, field, question, analysis):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    record = {"created_at": datetime.now(timezone.utc).isoformat(),
              "field": field, "question": question, "analysis": analysis}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def load_analyses(path, limit=20):
    file = Path(path)
    if not file.exists() or limit <= 0:
        return []
    records = []
    for line in file.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records[-limit:]
