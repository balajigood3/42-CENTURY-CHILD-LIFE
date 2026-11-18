import streamlit as st
from tamil_assistant.core import offline_answer, ollama_answer
from tamil_assistant.history import append_history, read_history

st.set_page_config(page_title="Tamil LLM Assistant", page_icon="தமிழ்", layout="centered")
st.title("தமிழ் LLM Assistant")
st.caption("தமிழில் கேள்வி கேளுங்கள். Offline demo அல்லது உங்கள் கணினியில் இயங்கும் Ollama model பயன்படுத்தலாம்.")
mode = st.radio("பதில் முறை", ["Offline demo", "Local Ollama"], horizontal=True)
model = st.text_input("Ollama model", "qwen2.5:3b", disabled=(mode != "Local Ollama"))
question = st.text_area("உங்கள் கேள்வி", placeholder="எ.கா. செயற்கை நுண்ணறிவு என்றால் என்ன?")
if st.button("பதில் உருவாக்கு", type="primary", disabled=not question.strip()):
    try:
        answer = ollama_answer(question, model) if mode == "Local Ollama" else offline_answer(question)
        st.markdown("### பதில்")
        st.write(answer)
        append_history("data/history.jsonl", question, answer)
    except RuntimeError as exc:
        st.error(str(exc))
st.divider()
with st.expander("சமீபத்திய உரையாடல்கள்"):
    for item in reversed(read_history("data/history.jsonl", 10)):
        st.markdown(f"**கேள்வி:** {item['question']}")
        st.write(item["answer"])
        st.caption(item["timestamp"])
