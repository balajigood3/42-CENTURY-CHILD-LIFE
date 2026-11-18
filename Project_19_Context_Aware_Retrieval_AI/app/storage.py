import sqlite3
from pathlib import Path

class ChunkStore:
    def __init__(self, path="data/context_retrieval.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS chunks(
                chunk_id TEXT PRIMARY KEY, source TEXT NOT NULL, category TEXT NOT NULL,
                text TEXT NOT NULL, chunk_index INTEGER, created_at TEXT)""")

    def replace_source(self, source, chunks):
        with sqlite3.connect(self.path) as db:
            db.execute("DELETE FROM chunks WHERE source=?", (source,))
            db.executemany("""INSERT OR REPLACE INTO chunks
                (chunk_id,source,category,text,chunk_index,created_at)
                VALUES(?,?,?,?,?,?)""",
                [(c["chunk_id"], c["source"], c["category"], c["text"],
                  c["chunk_index"], c["created_at"]) for c in chunks])

    def all_chunks(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("""SELECT chunk_id,source,category,text,chunk_index,created_at
                FROM chunks ORDER BY source,chunk_index""").fetchall()
        keys = ["chunk_id","source","category","text","chunk_index","created_at"]
        return [dict(zip(keys,row)) for row in rows]

    def sources(self):
        with sqlite3.connect(self.path) as db:
            return [r[0] for r in db.execute("SELECT DISTINCT source FROM chunks ORDER BY source")]

    def categories(self):
        with sqlite3.connect(self.path) as db:
            return [r[0] for r in db.execute("SELECT DISTINCT category FROM chunks ORDER BY category")]
