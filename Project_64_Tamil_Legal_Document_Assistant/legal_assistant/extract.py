from pathlib import Path

class DocumentError(ValueError):
    pass

def extract_text(path):
    p = Path(path)
    suffix = p.suffix.lower()
    if not p.is_file():
        raise DocumentError("File does not exist.")
    if suffix in {".txt", ".md"}:
        return p.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
        except Exception as exc:
            raise DocumentError(f"PDF extraction failed: {exc}") from exc
    if suffix == ".docx":
        try:
            from docx import Document
            doc = Document(p)
            content = [para.text for para in doc.paragraphs if para.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    content.append(" | ".join(cell.text.strip() for cell in row.cells))
            return "\n".join(content)
        except Exception as exc:
            raise DocumentError(f"DOCX extraction failed: {exc}") from exc
    raise DocumentError("Supported formats: TXT, MD, PDF, DOCX.")
