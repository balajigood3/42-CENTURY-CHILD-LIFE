from pathlib import Path
import json
from datetime import datetime, timezone

def append_history(path: str | Path, question: str, answer: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": datetime.now(timezone.utc).isoformat(),
              "question": question, "answer": answer}
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_history(path: str | Path, limit: int = 30) -> list[dict]:
    target = Path(path)
    if not target.exists():
        return []
    records = []
    for line in target.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records[-max(0, limit):]
