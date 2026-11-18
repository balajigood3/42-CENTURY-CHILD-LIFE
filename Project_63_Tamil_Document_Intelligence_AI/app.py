import streamlit as st
import tempfile
from pathlib import Path
from tamil_docs.assistant import inspect_document, ask_document
from tamil_docs.extractor import ExtractionError

st.set_page_config(page_title="Tamil Document Intelligence AI", layout="wide")
st.title("Tamil Document Intelligence AI")
st.caption("தமிழ் மற்றும் பல்மொழி ஆவணங்களைப் படித்து, தேடி, சுருக்கம் உருவாக்குங்கள்.")
upload = st.file_uploader("ஆவணத்தை பதிவேற்றவும்", type=["txt", "md", "docx", "pdf"])
if upload:
    suffix = Path(upload.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(upload.getvalue())
        temp_path = temp.name
    try:
        doc = inspect_document(temp_path)
        st.subheader("ஆவண விவரங்கள்")
        a, b, c = st.columns(3)
        a.metric("Characters", doc["characters"])
        b.metric("Words", doc["words"])
        c.metric("Chunks", len(doc["chunks"]))
        st.write("**Language:**", doc["language"])
        st.write("**Keywords:**", ", ".join(doc["keywords"]))
        st.subheader("சுருக்கம்")
        st.write(doc["summary"])
        question = st.text_input("இந்த ஆவணத்தைப் பற்றி கேள்வி கேளுங்கள்")
        if st.button("தேடு", disabled=not question.strip()):
            result = ask_document(doc, question)
            st.write(result["answer"])
            st.caption(result["grounding_note"])
        with st.expander("Extracted text preview"):
            st.text_area("Text", " ".join(doc["chunks"])[:6000], height=250)
    except ExtractionError as exc:
        st.error(str(exc))
    finally:
        Path(temp_path).unlink(missing_ok=True)
