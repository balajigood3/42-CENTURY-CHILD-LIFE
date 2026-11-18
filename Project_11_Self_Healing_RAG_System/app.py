import streamlit as st
from src.rag import SelfHealingRAG

st.set_page_config(page_title="Self-Healing RAG System",layout="wide")
st.title("Project 11 – Self-Healing RAG System")
st.caption("Local document RAG with retrieval diagnostics, query rewriting, and bounded retry.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    top_k=st.slider("Top K chunks",1,6,3)
    threshold=st.slider("Minimum retrieval score",0.0,1.0,0.12,0.01)
    st.caption("No paid API key. Ollama + local TF-IDF retrieval.")
rag=SelfHealingRAG(model,url,top_k=top_k,threshold=threshold)
if "docs" not in st.session_state: st.session_state.docs={}
uploads=st.file_uploader("Upload TXT / MD documents",type=["txt","md"],accept_multiple_files=True)
if uploads:
    for f in uploads:
        st.session_state.docs[f.name]=f.getvalue().decode("utf-8",errors="replace")
    st.success(f"{len(uploads)} file(s) loaded.")
if st.button("Clear documents"):
    st.session_state.docs={}; st.rerun()
question=st.text_input("உங்கள் கேள்வி")
if st.button("RAG Answer உருவாக்கு",type="primary"):
    if not st.session_state.docs: st.warning("முதலில் TXT அல்லது MD document upload செய்யவும்.")
    elif not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
    else:
        with st.spinner("Retrieve → diagnose → repair → answer..."):
            result=rag.ask(question,st.session_state.docs)
        st.subheader("பதில்")
        st.markdown(result["answer"])
        st.write("**Retrieval status:**",result["status"])
        with st.expander("RAG diagnostics"):
            st.json(result["diagnostics"])
            st.write("**Retrieved chunks**")
            for chunk in result["chunks"]: st.write(chunk)
st.info("Self-healing இங்கு retrieval/query repair மற்றும் retry-க்கு மட்டுமே. இது தவறான source document-ஐ தானாகச் சரிசெய்யாது.")
