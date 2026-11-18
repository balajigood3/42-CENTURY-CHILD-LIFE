import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/history.db")

class HistoryStore:
    def __init__(self, path=DB_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                goal TEXT,
                input_text TEXT NOT NULL,
                result_json TEXT NOT NULL
            )""")

    def _connect(self):
        return sqlite3.connect(self.path)

    def save(self, text, goal, result):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO analyses(created_at, goal, input_text, result_json) VALUES (?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), goal, text, json.dumps(result, ensure_ascii=False)),
            )

    def recent(self, limit=30):
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, created_at, goal, input_text, result_json FROM analyses ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [{"id": r["id"], "created_at": r["created_at"], "goal": r["goal"],
                 "input_text": r["input_text"], "result": json.loads(r["result_json"])} for r in rows]
