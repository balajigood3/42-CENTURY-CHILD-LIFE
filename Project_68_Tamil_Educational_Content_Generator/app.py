import streamlit as st
from edu_ai.generator import SUBJECTS, LEVELS, FORMATS, generate_content
from edu_ai.history import save_content, load_history

st.set_page_config(page_title="Tamil Educational Content Generator", layout="wide")
st.title("தமிழ் கல்வி உள்ளடக்க உருவாக்கி")
st.caption("பாடக்குறிப்புகள், விளக்கங்கள், வினா-விடைகள் மற்றும் பயிற்சித்தாள்களை உருவாக்குங்கள்.")
subject = st.selectbox("பாடப்பிரிவு", SUBJECTS)
topic = st.text_input("பாடத் தலைப்பு", placeholder="எ.கா. ஒளிச்சேர்க்கை")
level = st.selectbox("கற்றல் நிலை", LEVELS)
content_format = st.selectbox("உள்ளடக்க வடிவம்", FORMATS)
objective = st.text_input("கற்றல் நோக்கம் (விருப்பத்தேர்வு)")
mode_label = st.radio("உருவாக்கும் முறை", ["Sample mode", "Local Ollama LLM"], horizontal=True)
mode = "ollama" if mode_label == "Local Ollama LLM" else "sample"
model = st.text_input("Ollama model", "qwen2.5:3b", disabled=(mode == "sample"))
if st.button("கல்வி உள்ளடக்கம் உருவாக்கு", type="primary", disabled=not topic.strip()):
    try:
        result = generate_content(topic, subject, level, content_format,
                                  objective, mode=mode, model=model)
        st.session_state["edu_result"] = result
        save_content("data/history.jsonl", topic, subject, level,
                     content_format, result, mode)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
if st.session_state.get("edu_result"):
    st.subheader("உருவாக்கப்பட்ட உள்ளடக்கம்")
    st.markdown(st.session_state["edu_result"])
    st.download_button("Markdown பதிவிறக்கம்", st.session_state["edu_result"],
                       "tamil_learning_content.md", mime="text/markdown")
with st.expander("முந்தைய உள்ளடக்கங்கள்"):
    for row in reversed(load_history("data/history.jsonl", 10)):
        st.markdown(f"**{row['topic']} · {row['subject']} · {row['format']}**")
        st.markdown(row["content"])
