import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "history.db"

def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                initial_answer TEXT NOT NULL,
                final_answer TEXT NOT NULL,
                score INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_history(question, initial_answer, final_answer, score, status):
    initialize_database()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO history (question, initial_answer, final_answer, score, status)
            VALUES (?, ?, ?, ?, ?)
        """, (question, initial_answer, final_answer, score, status))

def get_history(limit=50):
    initialize_database()
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT id, question, initial_answer, final_answer, score, status, created_at
            FROM history ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
