import streamlit as st
from multimodal_rag import (
    extract_image_text, chunk_text, build_index, retrieve, answer_with_context,
    validate_upload
)

st.set_page_config(page_title="Multimodal RAG Engine", page_icon="🔎", layout="wide")
st.title("Multimodal RAG Engine")
st.caption("Index text documents and images, retrieve relevant evidence, and generate grounded answers. No paid API keys.")

with st.sidebar:
    st.header("Index settings")
    st.caption("Images are indexed through OCR text extraction. Optional OCR requires Tesseract.")
    top_k = st.slider("Retrieved chunks", 1, 8, 4)

uploads = st.file_uploader(
    "Upload knowledge sources",
    type=["txt", "md", "pdf", "png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if st.button("Build knowledge index", type="primary", disabled=not uploads):
    records = []
    errors = []
    for uploaded in uploads:
        try:
            validate_upload(uploaded.name, uploaded.size)
            ext = uploaded.name.lower().rsplit(".", 1)[-1]
            if ext in {"txt", "md"}:
                text = uploaded.getvalue().decode("utf-8", errors="replace")
            elif ext == "pdf":
                try:
                    from pypdf import PdfReader
                    import io
                    reader = PdfReader(io.BytesIO(uploaded.getvalue()))
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
                except ImportError:
                    errors.append(f"{uploaded.name}: install pypdf to parse PDFs.")
                    continue
            else:
                try:
                    text = extract_image_text(uploaded.getvalue())
                except RuntimeError as exc:
                    errors.append(f"{uploaded.name}: {exc}")
                    continue
            records.extend(chunk_text(text, source=uploaded.name))
        except Exception as exc:
            errors.append(f"{uploaded.name}: {exc}")
    st.session_state["rag_chunks"] = records
    if errors:
        for error in errors:
            st.warning(error)
    st.success(f"Indexed {len(records)} text chunks.")

if "rag_chunks" in st.session_state:
    st.caption(f"Current index: {len(st.session_state['rag_chunks'])} chunks")
    question = st.text_input("Ask a question about your sources")
    if st.button("Retrieve and answer", disabled=not question.strip()):
        hits = retrieve(question, st.session_state["rag_chunks"], top_k=top_k)
        st.session_state["rag_result"] = answer_with_context(question, hits)
    if "rag_result" in st.session_state:
        result = st.session_state["rag_result"]
        st.subheader("Grounded answer")
        st.write(result["answer"])
        st.subheader("Retrieved evidence")
        for hit in result["sources"]:
            with st.expander(f"{hit['source']} · score {hit['score']}"):
                st.write(hit["text"])
