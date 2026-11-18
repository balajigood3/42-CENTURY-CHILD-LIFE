from pathlib import Path
from datetime import datetime, timezone
import json

def append_record(path, record):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"created_at": datetime.now(timezone.utc).isoformat(), **record}
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False) + "\n")

def recent_records(path, limit=30):
    target = Path(path)
    if not target.exists() or limit < 1:
        return []
    records = []
    for line in target.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records[-limit:]
