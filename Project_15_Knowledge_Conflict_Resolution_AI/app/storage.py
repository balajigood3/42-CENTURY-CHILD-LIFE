import sqlite3,json
from pathlib import Path
class Store:
    def __init__(self,path="data/history.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY, created_at TEXT DEFAULT CURRENT_TIMESTAMP, source_names TEXT, claims_json TEXT, report TEXT)")
    def save(self,names,claims,report):
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO analyses(source_names,claims_json,report) VALUES(?,?,?)",(json.dumps(names),json.dumps(claims,ensure_ascii=False),report))
    def recent(self,limit=20):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT id,created_at,source_names FROM analyses ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
