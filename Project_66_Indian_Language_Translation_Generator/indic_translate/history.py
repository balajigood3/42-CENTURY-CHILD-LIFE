from pathlib import Path
import json
from datetime import datetime, timezone

def save_translation(path, source_text, translated_text, source_lang, target_lang):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    item = {"timestamp": datetime.now(timezone.utc).isoformat(),
            "source_language": source_lang, "target_language": target_lang,
            "source_text": source_text, "translated_text": translated_text}
    with file.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")

def load_history(path, limit=30):
    file = Path(path)
    if not file.exists():
        return []
    rows = []
    for line in file.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-max(0, limit):]
