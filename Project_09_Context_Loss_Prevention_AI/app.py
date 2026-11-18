import streamlit as st
from src.context_manager import ContextManager

st.set_page_config(page_title="Context Loss Prevention AI",layout="wide")
st.title("Context Loss Prevention AI")
st.caption("நீண்ட உரையாடல்களில் முக்கிய விவரங்களைச் சுருக்கி, பின்னர் வரும் கேள்விகளுக்கு context-ஐ மீட்டெடுக்கும் local GenAI பயன்பாடு.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    max_chars=st.slider("Context chunk size (characters)",500,4000,1800,100)
    st.caption("Paid API key தேவையில்லை. `ollama pull qwen2.5:3b` இயக்கவும்.")
manager=ContextManager(model,url,max_chars=max_chars)
if "messages" not in st.session_state: st.session_state.messages=[]
if "memory" not in st.session_state: st.session_state.memory=""
if "chunks" not in st.session_state: st.session_state.chunks=[]
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])
user_text=st.chat_input("செய்தி அல்லது கேள்வியை உள்ளிடவும்")
if user_text:
    st.session_state.messages.append({"role":"user","content":user_text})
    with st.chat_message("user"): st.markdown(user_text)
    with st.chat_message("assistant"):
        with st.spinner("Context புதுப்பிக்கப்படுகிறது..."):
            st.session_state.chunks=manager.add_text(st.session_state.chunks,user_text)
            st.session_state.memory=manager.build_memory(st.session_state.chunks,st.session_state.memory)
            answer=manager.answer(user_text,st.session_state.memory,st.session_state.chunks)
        st.markdown(answer)
    st.session_state.messages.append({"role":"assistant","content":answer})
with st.expander("சேமிக்கப்பட்ட context memory"):
    st.text_area("Memory",st.session_state.memory,height=220)
    st.write(f"Context chunks: {len(st.session_state.chunks)}")
    if st.button("உரையாடல் memory-ஐ அழி"):
        st.session_state.messages=[]; st.session_state.memory=""; st.session_state.chunks=[]
        st.rerun()
st.info("Memory என்பது சுருக்கப்பட்ட context. முழு உரையாடலின் ஒவ்வொரு விவரமும் பாதுகாக்கப்படும் என உத்தரவாதமில்லை.")
