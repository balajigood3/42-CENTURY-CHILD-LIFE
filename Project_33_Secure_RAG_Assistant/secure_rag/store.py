from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable
from .security import normalize_role

DB_PATH = Path(__file__).resolve().parent.parent / "secure_rag.db"

def connect(db_path: str | Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str | Path = DB_PATH):
    with connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_name TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                allowed_roles TEXT NOT NULL,
                UNIQUE(doc_name, chunk_index)
            )
        """)

def add_document(doc_name: str, text: str, allowed_roles: Iterable[str], db_path: str | Path = DB_PATH):
    roles = sorted(set(allowed_roles))
    if not roles or not set(roles).issubset({"admin", "staff", "user"}):
        raise ValueError("Choose one or more valid roles: admin, staff, user")
    chunks = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not chunks:
        raise ValueError("Document contains no readable text.")
    with connect(db_path) as conn:
        conn.execute("DELETE FROM chunks WHERE doc_name = ?", (doc_name,))
        conn.executemany(
            "INSERT INTO chunks(doc_name, chunk_index, content, allowed_roles) VALUES (?, ?, ?, ?)",
            [(doc_name, i, chunk, ",".join(roles)) for i, chunk in enumerate(chunks)]
        )
    return len(chunks)

def list_documents(db_path: str | Path = DB_PATH):
    with connect(db_path) as conn:
        rows = conn.execute("""
            SELECT doc_name, COUNT(*) AS chunk_count, GROUP_CONCAT(DISTINCT allowed_roles) AS roles
            FROM chunks GROUP BY doc_name ORDER BY doc_name
        """).fetchall()
    return [dict(row) for row in rows]

def delete_document(doc_name: str, db_path: str | Path = DB_PATH):
    with connect(db_path) as conn:
        conn.execute("DELETE FROM chunks WHERE doc_name = ?", (doc_name,))

def get_authorized_chunks(role: str, db_path: str | Path = DB_PATH):
    role = normalize_role(role)
    # ACL filtering occurs in SQL before any ranking or content is returned.
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, doc_name, chunk_index, content FROM chunks "
            "WHERE ',' || allowed_roles || ',' LIKE ? ORDER BY doc_name, chunk_index",
            (f"%,{role},%",)
        ).fetchall()
    return [dict(row) for row in rows]
