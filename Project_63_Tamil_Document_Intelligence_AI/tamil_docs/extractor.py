"""Text extraction for plain text, Markdown, DOCX, and PDF files."""
from pathlib import Path

SUPPORTED = {".txt", ".md", ".docx", ".pdf"}

class ExtractionError(ValueError):
    pass

def extract_text(path: str | Path) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ExtractionError(f"Unsupported file type: {suffix or 'no extension'}")
    if not file_path.is_file():
        raise ExtractionError("File does not exist.")
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".docx":
        try:
            from docx import Document
            document = Document(file_path)
            parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    parts.append(" | ".join(cell.text.strip() for cell in row.cells))
            return "\n".join(parts)
        except Exception as exc:
            raise ExtractionError(f"Could not read DOCX: {exc}") from exc
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            raise ExtractionError(f"Could not read PDF: {exc}") from exc
    raise ExtractionError("Unsupported file type.")
