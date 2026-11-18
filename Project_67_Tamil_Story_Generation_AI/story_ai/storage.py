from pathlib import Path
import json
from datetime import datetime, timezone

def save_story(path, topic, genre, story, mode):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    row = {"created_at": datetime.now(timezone.utc).isoformat(),
           "topic": topic, "genre": genre, "mode": mode, "story": story}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")

def recent_stories(path, limit=10):
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
