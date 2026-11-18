import streamlit as st
from code_mixed.assistant import answer
from code_mixed.history import save_record, load_records

st.set_page_config(page_title="Tamil Code-Mixed AI", page_icon="தமிழ்")
st.title("Tamil Code-Mixed AI")
st.caption("தமிழ் + English + Tanglish கேள்விகளைப் புரிந்துகொள்ளும் assistant.")
mode = st.radio("Mode", ["Offline demo", "Local Ollama"], horizontal=True)
model = st.text_input("Local model", "qwen2.5:3b", disabled=(mode != "Local Ollama"))
prompt = st.text_area("உங்கள் கேள்வி / Your question",
                      placeholder="Example: RAG na enna? simple ah sollu")
if st.button("Submit", type="primary", disabled=not prompt.strip()):
    try:
        result = answer(prompt, use_local=(mode == "Local Ollama"), model=model)
        st.subheader("பதில் / Answer")
        st.write(result["answer"])
        st.caption(f"Input type: {result['script_mix']['label']}")
        with st.expander("Normalization details"):
            st.write(result["normalized_hint"])
            st.json(result["script_mix"])
        save_record("data/history.jsonl", prompt, result["answer"])
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
with st.expander("Recent conversations"):
    for row in reversed(load_records("data/history.jsonl", 10)):
        st.markdown(f"**You:** {row['user']}")
        st.write(row["assistant"])
