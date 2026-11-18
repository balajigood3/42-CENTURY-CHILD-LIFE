import json,sqlite3
from pathlib import Path

class PreferenceStore:
    def __init__(self,path="data/preferences.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS prefs (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)")
    def save(self,prefs):
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO prefs(id,data) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",
                       (json.dumps(prefs,ensure_ascii=False),))
    def load(self):
        with sqlite3.connect(self.path) as db: row=db.execute("SELECT data FROM prefs WHERE id=1").fetchone()
        return json.loads(row[0]) if row else None
