from pathlib import Path
from datetime import datetime, timezone
import json

def save_content(path, topic, subject, level, content_format, content, mode):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    row = {"created_at": datetime.now(timezone.utc).isoformat(),
           "topic": topic, "subject": subject, "level": level,
           "format": content_format, "mode": mode, "content": content}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")

def load_history(path, limit=10):
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
