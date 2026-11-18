import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone

class MemoryStore:
    def __init__(self,path="data/memory.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS memories(
              id INTEGER PRIMARY KEY AUTOINCREMENT, memory TEXT NOT NULL,
              normalized TEXT UNIQUE NOT NULL, category TEXT, importance INTEGER,
              confidence REAL, source TEXT, created_at TEXT, updated_at TEXT,
              active INTEGER DEFAULT 1)""")
    def add_many(self,items):
        now=datetime.now(timezone.utc).isoformat()
        added=0
        with sqlite3.connect(self.path) as db:
            for m in items:
                normalized=" ".join(m["memory"].strip().casefold().split())
                if not normalized: continue
                cur=db.execute("""INSERT INTO memories(memory,normalized,category,importance,
                    confidence,source,created_at,updated_at,active)
                    VALUES(?,?,?,?,?,?,?,?,1)
                    ON CONFLICT(normalized) DO UPDATE SET
                    memory=excluded.memory,category=excluded.category,
                    importance=MAX(memories.importance,excluded.importance),
                    confidence=excluded.confidence,source=excluded.source,
                    updated_at=excluded.updated_at,active=1""",
                    (m["memory"],normalized,m.get("category","general"),m.get("importance",3),
                     m.get("confidence",0),m.get("source","unknown"),now,now))
                if cur.rowcount: added+=1
        return added
    def all(self,include_inactive=False):
        query="SELECT id,memory,category,importance,confidence,source,created_at,updated_at,active FROM memories"
        if not include_inactive: query+=" WHERE active=1"
        query+=" ORDER BY importance DESC, updated_at DESC"
        with sqlite3.connect(self.path) as db:
            rows=db.execute(query).fetchall()
        keys=["id","memory","category","importance","confidence","source","created_at","updated_at","active"]
        return [dict(zip(keys,row)) for row in rows]
    def deactivate(self,memory_id):
        with sqlite3.connect(self.path) as db:
            cur=db.execute("UPDATE memories SET active=0,updated_at=? WHERE id=?",
                           (datetime.now(timezone.utc).isoformat(),memory_id))
        return cur.rowcount>0
    def clear_all(self):
        with sqlite3.connect(self.path) as db: db.execute("DELETE FROM memories")
    def count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT COUNT(*) FROM memories WHERE active=1").fetchone()[0]
