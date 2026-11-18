from pathlib import Path
from datetime import datetime, timezone
import json

def append_turn(path, user_text, assistant_text):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now(timezone.utc).isoformat(),
           "user": user_text, "assistant": assistant_text}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_turns(path, limit=30):
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
