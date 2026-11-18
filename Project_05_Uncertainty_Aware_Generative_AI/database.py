import sqlite3, json
from pathlib import Path
DB_PATH = Path(__file__).parent / "data" / "uncertainty_history.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL, uncertainty_level TEXT NOT NULL,
            answer TEXT NOT NULL, result_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

def save_analysis(question, result):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO analyses
        (question, uncertainty_level, answer, result_json) VALUES (?, ?, ?, ?)""",
        (question, result["uncertainty_level"], result["answer"],
         json.dumps(result, ensure_ascii=False)))

def get_history(limit=30):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""SELECT created_at, question, uncertainty_level, answer
        FROM analyses ORDER BY id DESC LIMIT ?""", (limit,)).fetchall()
