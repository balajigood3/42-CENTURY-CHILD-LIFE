# Project 64 — Tamil Legal Document Assistant

தமிழ் மற்றும் English legal documents-இல் பொதுவான clause தலைப்புகளை அடையாளம் கண்டு, review checklist மற்றும் searchable passages உருவாக்கும் ஆரம்பநிலை உதவி கருவி.

## Features
- TXT, Markdown, PDF, DOCX extraction
- Termination, indemnity, liability, confidentiality, payment, renewal, governing law, data protection, IP clause spotting
- Keyword-based passage search
- Markdown and JSON review reports
- Streamlit UI, Docker, pytest

## Setup
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Open http://localhost:8501.

## Tests
```bash
pytest -q
```

## Docker
```bash
docker compose up --build
```

## Architecture
Upload → `extract.py` → `analyzer.py` + `qa.py` → Streamlit → downloadable review report.

## Important limitations
- This is automated issue-spotting, not legal advice, legal representation, or a determination of enforceability.
- Regex checks can miss clauses, misunderstand context, or flag irrelevant text.
- Clause presence/absence is not proof of adequacy or risk level.
- Have a qualified lawyer review the complete document, jurisdiction, facts, schedules, and amendments.
- Scanned PDFs require OCR; this version extracts embedded PDF text only.
- No paid API keys are used.
