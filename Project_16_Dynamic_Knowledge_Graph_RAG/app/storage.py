import json, sqlite3
from pathlib import Path

class GraphStore:
    def __init__(self, path="data/knowledge.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS documents(
                name TEXT PRIMARY KEY, content_hash TEXT, graph_json TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    def upsert(self, name, content_hash, graph_data):
        with sqlite3.connect(self.path) as db:
            db.execute("""INSERT INTO documents(name,content_hash,graph_json,updated_at)
                VALUES(?,?,?,CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET content_hash=excluded.content_hash,
                graph_json=excluded.graph_json,updated_at=CURRENT_TIMESTAMP""",
                (name, content_hash, json.dumps(graph_data, ensure_ascii=False)))

    def load_all(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT name,graph_json FROM documents ORDER BY name").fetchall()
        return [(name, json.loads(data)) for name, data in rows]

    def names(self):
        return [name for name, _ in self.load_all()]
