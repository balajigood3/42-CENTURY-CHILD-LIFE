import streamlit as st
from src.reasoner import MultiDocumentReasoner

st.set_page_config(page_title="Multi-Document Reasoning AI",layout="wide")
st.title("Project 13 – Multi-Document Reasoning AI")
st.caption("பல ஆவணங்களில் உள்ள தகவல்களை ஒப்பிட்டு, ஒருங்கிணைத்து, ஆதாரங்களுடன் பதிலளிக்கும் Local GenAI system.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    top_k=st.slider("Passages per document",1,4,2)
    st.caption("Paid API key இல்லை. Ollama local model பயன்படுத்தப்படுகிறது.")
uploads=st.file_uploader("TXT / MD ஆவணங்களை upload செய்யவும்",type=["txt","md"],accept_multiple_files=True)
question=st.text_area("கேள்வி / ஒப்பீட்டு பணி",height=110,placeholder="ஆவணங்களில் உள்ள கருத்துகளை ஒப்பிட்டு வேறுபாடுகளை விளக்கவும்.")
if st.button("Multi-document reasoning",type="primary"):
    if not uploads: st.warning("குறைந்தது இரண்டு ஆவணங்களை upload செய்யவும்.")
    elif len(uploads)<2: st.warning("இந்த project-க்கு குறைந்தது இரண்டு ஆவணங்கள் தேவை.")
    elif not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
    else:
        docs={f.name:f.getvalue().decode("utf-8",errors="replace") for f in uploads}
        engine=MultiDocumentReasoner(model,url,top_k=top_k)
        with st.spinner("ஆவணங்களைத் தேடி ஒப்பிடுகிறது..."):
            result=engine.reason(question,docs)
        st.subheader("ஒருங்கிணைந்த பதில்")
        st.markdown(result["answer"])
        with st.expander("Document-wise evidence"):
            for name,passages in result["evidence"].items():
                st.markdown(f"**{name}**")
                for p in passages: st.write(f"- Score {p['score']}: {p['text']}")
        with st.expander("Coverage diagnostics"):
            st.json(result["coverage"])
st.info("இந்த app retrieval செய்யப்பட்ட passages-ஐ மட்டுமே பயன்படுத்துமாறு model-க்கு அறிவுறுத்துகிறது; முழு ஆவணங்களின் exhaustive review எனக் கருத வேண்டாம்.")
