import sqlite3
import json
from pathlib import Path

DB = Path(__file__).parent / "data" / "reasoning_history.db"

def initialize_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem TEXT NOT NULL,
            final_answer TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")

def save_run(problem, result):
    initialize_db()
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO runs (problem, final_answer, result_json) VALUES (?, ?, ?)",
            (problem, result["final_answer"], json.dumps(result, ensure_ascii=False))
        )

def list_runs(limit=25):
    initialize_db()
    with sqlite3.connect(DB) as conn:
        return conn.execute(
            "SELECT created_at, problem, final_answer FROM runs ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
