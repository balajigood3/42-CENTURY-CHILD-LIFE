from __future__ import annotations
from pathlib import Path
from .store import add_document

def extract_text(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        return data.decode("utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            import io
            reader = PdfReader(io.BytesIO(data))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ValueError(f"Could not read PDF: {type(exc).__name__}") from exc
    raise ValueError("Supported formats: TXT, MD, CSV, PDF")

def ingest_file(filename: str, data: bytes, allowed_roles, db_path=None):
    text = extract_text(filename, data)
    if db_path:
        return add_document(filename, text, allowed_roles, db_path)
    return add_document(filename, text, allowed_roles)
