import streamlit as st
from src.knowledge_base import AutonomousKnowledgeBase

st.set_page_config(page_title="Autonomous Knowledge Base",layout="wide")
st.title("Project 12 – Autonomous Knowledge Base")
st.caption("ஆவணங்களை index செய்து, knowledge base-ஐ புதுப்பித்து, ஆதாரங்களுடன் கேள்விகளுக்கு பதிலளிக்கும் local GenAI app.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    st.caption("Paid API key இல்லை. `ollama pull qwen2.5:3b` இயக்கவும்.")
kb=AutonomousKnowledgeBase(model,url)
tab1,tab2=st.tabs(["Knowledge Base","Ask"])
with tab1:
    uploads=st.file_uploader("TXT / MD documents upload",type=["txt","md"],accept_multiple_files=True)
    if st.button("Ingest / Update Knowledge Base",type="primary"):
        if not uploads: st.warning("குறைந்தது ஒரு document upload செய்யவும்.")
        else:
            with st.spinner("Documents index செய்யப்படுகின்றன..."):
                stats=kb.ingest(uploads)
            st.success(f"புதிய chunks: {stats['added']} | மொத்த chunks: {stats['total']}")
    st.write("**Stored knowledge base documents**")
    docs=kb.list_documents()
    if docs:
        for d in docs: st.write(f"- {d['name']} · {d['chunks']} chunks · {d['updated_at']}")
    else: st.info("இன்னும் documents index செய்யப்படவில்லை.")
    if st.button("Delete entire knowledge base"):
        kb.clear()
        st.warning("Knowledge base அழிக்கப்பட்டது.")
with tab2:
    question=st.text_input("Knowledge base-ஐக் கேளுங்கள்")
    top_k=st.slider("Retrieved passages",1,8,4)
    if st.button("Answer from knowledge base"):
        if not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
        else:
            with st.spinner("Relevant knowledge தேடப்படுகிறது..."):
                result=kb.ask(question,top_k)
            st.markdown(result["answer"])
            st.write("**Status:**",result["status"])
            with st.expander("Sources / retrieved passages"):
                for item in result["sources"]:
                    st.markdown(f"**{item['source']} · score {item['score']}**")
                    st.write(item["text"])
st.caption("இந்த version local SQLite + lexical retrieval பயன்படுத்துகிறது. Knowledge base update என்பது upload செய்யப்பட்ட ஆவணங்களை index செய்வதாகும்.")
