import streamlit as st
from src.pdf_engine import IntelligentPDFEngine

st.set_page_config(page_title="Intelligent PDF Understanding AI",layout="wide")
st.title("Project 14 – Intelligent PDF Understanding AI")
st.caption("PDF-களின் உள்ளடக்கத்தைப் புரிந்து, பக்க ஆதாரங்களுடன் கேள்விகளுக்குப் பதிலளிக்கும் Local GenAI application.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    top_k=st.slider("Retrieved passages",1,8,4)
    st.caption("Paid API key இல்லை. Ollama local model பயன்படுத்தப்படுகிறது.")
uploads=st.file_uploader("PDF documents upload",type=["pdf"],accept_multiple_files=True)
if uploads:
    engine=IntelligentPDFEngine(model,url,top_k)
    if st.button("PDF-களை ஆய்வு செய்து index செய்",type="primary"):
        with st.spinner("PDF text மற்றும் page metadata extract செய்யப்படுகிறது..."):
            docs={}
            errors=[]
            for f in uploads:
                try: docs[f.name]=engine.extract_pdf(f.getvalue())
                except Exception as e: errors.append(f"{f.name}: {e}")
            st.session_state["pdf_docs"]=docs
            st.session_state["pdf_errors"]=errors
        st.success(f"வெற்றிகரமாக extract செய்யப்பட்ட PDF-கள்: {len(docs)}")
        for err in errors: st.error(err)
if "pdf_docs" in st.session_state:
    docs=st.session_state["pdf_docs"]
    for name,data in docs.items():
        with st.expander(f"{name} · {data['page_count']} pages"):
            st.write(f"Extracted characters: {len(data['text'])}")
            st.text(data["text"][:2500] or "Text கிடைக்கவில்லை. இது scanned PDF ஆக இருக்கலாம்.")
    question=st.text_area("PDF-களிடம் கேள்வி கேளுங்கள்",placeholder="இந்த ஆவணத்தின் முக்கிய நோக்கம் என்ன? எந்த பக்கத்தில் குறிப்பிடப்பட்டுள்ளது?")
    if st.button("PDF-களிலிருந்து பதில் உருவாக்கு"):
        if not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
        else:
            engine=IntelligentPDFEngine(model,url,top_k)
            with st.spinner("Relevant pages தேடப்பட்டு பதில் உருவாக்கப்படுகிறது..."):
                result=engine.ask(question,docs)
            st.subheader("பதில்")
            st.markdown(result["answer"])
            st.write("**Status:**",result["status"])
            with st.expander("Page-level sources"):
                for hit in result["sources"]:
                    st.markdown(f"**{hit['source']} — Page {hit['page']} · score {hit['score']}**")
                    st.write(hit["text"])
st.info("Scanned/image-only PDF-களுக்கு OCR தேவை. இந்த version text-based PDF-களை ஆதரிக்கிறது.")
