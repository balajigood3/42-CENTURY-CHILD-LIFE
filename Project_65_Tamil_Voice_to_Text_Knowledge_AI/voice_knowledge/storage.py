from pathlib import Path
import json

def save_note(note: dict, directory: str | Path = "knowledge"):
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in note["source"])
    target = folder / f"{safe_name}.json"
    target.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    return target

def load_notes(directory: str | Path = "knowledge") -> list[dict]:
    folder = Path(directory)
    if not folder.exists():
        return []
    notes = []
    for file in folder.glob("*.json"):
        try:
            notes.append(json.loads(file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return notes
