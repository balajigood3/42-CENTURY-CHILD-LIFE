import fitz
from src.pdf_engine import IntelligentPDFEngine

def make_pdf():
    doc=fitz.open()
    page=doc.new_page()
    page.insert_text((72,72),"RAG combines retrieval and generation. This page explains document search.")
    data=doc.tobytes()
    doc.close()
    return data

def test_extract_pdf_has_page_numbers():
    result=IntelligentPDFEngine.extract_pdf(make_pdf())
    assert result["page_count"]==1
    assert "retrieval and generation" in result["pages"][0]["text"]
    assert result["pages"][0]["page"]==1

def test_retrieve_returns_source_page():
    engine=IntelligentPDFEngine(top_k=2)
    docs={"guide.pdf":IntelligentPDFEngine.extract_pdf(make_pdf())}
    hits=engine.retrieve("RAG retrieval generation",docs)
    assert hits
    assert hits[0]["source"]=="guide.pdf"
    assert hits[0]["page"]==1

def test_empty_pdf_text_returns_no_retrieval():
    engine=IntelligentPDFEngine()
    docs={"empty.pdf":{"pages":[{"page":1,"text":""}]}}
    assert engine.retrieve("find a topic",docs)==[]
