import json,sqlite3
from pathlib import Path
DB_PATH=Path(__file__).parent/"data"/"contradictions.db"
def init_db():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB_PATH) as c: c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, source_a TEXT NOT NULL, source_b TEXT NOT NULL, status TEXT NOT NULL, summary TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
def save_result(a,b,result):
    init_db()
    with sqlite3.connect(DB_PATH) as c: c.execute("INSERT INTO reports(source_a,source_b,status,summary,result_json) VALUES(?,?,?,?,?)",(a,b,result["overall_status"],result["summary"],json.dumps(result,ensure_ascii=False)))
def get_history(limit=30):
    init_db()
    with sqlite3.connect(DB_PATH) as c: return c.execute("SELECT created_at,source_a,source_b,status,summary FROM reports ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
