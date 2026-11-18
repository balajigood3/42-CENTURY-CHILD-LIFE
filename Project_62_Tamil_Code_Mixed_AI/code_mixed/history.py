from pathlib import Path
import json
from datetime import datetime, timezone

def save_record(path, user_text, assistant_text):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    item = {"time": datetime.now(timezone.utc).isoformat(),
            "user": user_text, "assistant": assistant_text}
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")

def load_records(path, limit=25):
    target = Path(path)
    if not target.exists():
        return []
    result = []
    for line in target.read_text(encoding="utf-8").splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return result[-max(0, limit):]
