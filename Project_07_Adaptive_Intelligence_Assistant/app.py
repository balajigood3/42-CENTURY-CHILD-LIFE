import streamlit as st
from src.assistant import AdaptiveAssistant
from src.store import PreferenceStore

st.set_page_config(page_title="Adaptive Intelligence Assistant", layout="wide")
st.title("Adaptive Intelligence Assistant")
st.caption("உங்கள் மொழி, தொனி, பதில் நீளத்திற்கு ஏற்ப பதிலை மாற்றும் Local LLM பயன்பாடு.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    tone=st.selectbox("பதில் தொனி",["Clear and professional","Friendly","Academic","Concise"])
    detail=st.selectbox("விவர அளவு",["Short","Balanced","Detailed"])
    language=st.selectbox("மொழி",["Tamil","English","Tamil + English"])
    save=st.checkbox("விருப்பங்களை உள்ளூரில் சேமி",True)
prefs={"tone":tone,"detail":detail,"language":language}
store=PreferenceStore()
if save: store.save(prefs)
assistant=AdaptiveAssistant(model,url)
question=st.text_area("உங்கள் கேள்வி",height=160)
if st.button("பதில் உருவாக்கு",type="primary"):
    if question.strip():
        with st.spinner("பதில் உருவாக்கப்படுகிறது..."):
            st.markdown(assistant.respond(question,prefs))
    else: st.warning("கேள்வியை உள்ளிடவும்.")
st.caption("முக்கியமான தகவல்களைச் சரிபார்க்கவும்; LLM பதில்கள் தவறாக இருக்கலாம்.")
