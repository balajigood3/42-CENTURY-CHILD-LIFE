import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "reports.db"

def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            original_answer TEXT NOT NULL,
            status TEXT NOT NULL,
            corrected_answer TEXT NOT NULL,
            report_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

def save_report(question, original_answer, result):
    initialize_database()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""INSERT INTO reports
        (question, original_answer, status, corrected_answer, report_json)
        VALUES (?, ?, ?, ?, ?)""",
        (question, original_answer, result["overall_status"],
         result["corrected_answer"], json.dumps(result, ensure_ascii=False)))

def get_reports(limit=30):
    initialize_database()
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
        SELECT created_at, question, status, corrected_answer
        FROM reports ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
