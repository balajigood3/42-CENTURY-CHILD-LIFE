import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class KnowledgeStore:
    def __init__(self, path="data/continuous_knowledge.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS documents(
                id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL,
                version INTEGER NOT NULL, content_hash TEXT NOT NULL,
                created_at TEXT NOT NULL, active INTEGER DEFAULT 1,
                UNIQUE(source,version))""")
            db.execute("""CREATE TABLE IF NOT EXISTS chunks(
                id INTEGER PRIMARY KEY AUTOINCREMENT, chunk_id TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL, version INTEGER NOT NULL, chunk_index INTEGER,
                text TEXT NOT NULL, created_at TEXT NOT NULL, active INTEGER DEFAULT 1)""")
            db.execute("""CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT, chunk_db_id INTEGER NOT NULL,
                rating INTEGER NOT NULL, comment TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY(chunk_db_id) REFERENCES chunks(id))""")

    def ingest(self, source, content_hash, chunks):
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.path) as db:
            row = db.execute("SELECT MAX(version) FROM documents WHERE source=?", (source,)).fetchone()
            latest = row[0] or 0
            old = db.execute("SELECT content_hash FROM documents WHERE source=? AND version=?",
                             (source, latest)).fetchone() if latest else None
            if old and old[0] == content_hash:
                return latest, 0, False
            version = latest + 1
            db.execute("UPDATE documents SET active=0 WHERE source=?", (source,))
            db.execute("UPDATE chunks SET active=0 WHERE source=?", (source,))
            db.execute("INSERT INTO documents(source,version,content_hash,created_at,active) VALUES(?,?,?,?,1)",
                       (source, version, content_hash, now))
            for c in chunks:
                db.execute("""INSERT INTO chunks(chunk_id,source,version,chunk_index,text,created_at,active)
                    VALUES(?,?,?,?,?,?,1)""",
                    (c["chunk_id"], source, version, c["chunk_index"], c["text"], now))
            return version, len(chunks), True

    def active_chunks(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("""SELECT id,chunk_id,source,version,chunk_index,text,created_at
                FROM chunks WHERE active=1 ORDER BY source,chunk_index""").fetchall()
        keys = ["id","chunk_id","source","version","chunk_index","text","created_at"]
        return [dict(zip(keys,r)) for r in rows]

    def add_feedback(self, chunk_db_id, rating, comment=""):
        if not 1 <= int(rating) <= 5:
            raise ValueError("Rating must be from 1 to 5")
        with sqlite3.connect(self.path) as db:
            exists = db.execute("SELECT 1 FROM chunks WHERE id=?", (chunk_db_id,)).fetchone()
            if not exists:
                raise ValueError("Chunk not found")
            db.execute("INSERT INTO feedback(chunk_db_id,rating,comment,created_at) VALUES(?,?,?,?)",
                       (chunk_db_id, int(rating), comment,
                        datetime.now(timezone.utc).isoformat()))

    def feedback_summary(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("""SELECT chunk_db_id,AVG(rating),COUNT(*)
                FROM feedback GROUP BY chunk_db_id""").fetchall()
        return {int(i): {"avg_rating": float(avg), "count": int(count)}
                for i,avg,count in rows}

    def stats(self):
        with sqlite3.connect(self.path) as db:
            docs = db.execute("SELECT COUNT(*) FROM documents WHERE active=1").fetchone()[0]
            chunks = db.execute("SELECT COUNT(*) FROM chunks WHERE active=1").fetchone()[0]
            versions = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            fb = db.execute("SELECT COUNT(*),AVG(rating) FROM feedback").fetchone()
        return {"documents":docs,"chunks":chunks,"versions":versions,
                "feedback_count":fb[0] or 0,"average_rating":fb[1] or 0.0}

    def document_versions(self):
        with sqlite3.connect(self.path) as db:
            return db.execute("""SELECT source,version,created_at,active
                FROM documents ORDER BY source,version DESC""").fetchall()
