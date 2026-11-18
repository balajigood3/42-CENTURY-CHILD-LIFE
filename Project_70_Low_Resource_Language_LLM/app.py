import streamlit as st
from lowres_llm.language import LANGUAGES, detect_script
from lowres_llm.prompting import TASKS
from lowres_llm.provider import generate
from lowres_llm.evaluation import basic_output_checks, script_match_ratio
from lowres_llm.history import save_record, load_records

st.set_page_config(page_title="Low-Resource Language LLM", layout="wide")
st.title("Low-Resource Language LLM Assistant")
st.caption("குறைந்த தரவுள்ள மொழிகளுக்கான local multilingual LLM workflow. Paid API key தேவையில்லை.")

language = st.selectbox("Output language", list(LANGUAGES))
task = st.selectbox("Task", TASKS)
model = st.text_input("Local Ollama model", "qwen2.5:3b")
source = st.text_area("Input text / question", height=160)
context = st.text_area("Optional context", height=80)
if source.strip():
    st.caption(f"Detected input script: {detect_script(source)}")

if st.button("Generate", type="primary", disabled=not source.strip()):
    try:
        output = generate(source, language, task, context, model)
        st.session_state["result"] = output
        save_record("data/history.jsonl", language, task, source, output)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

if st.session_state.get("result"):
    output = st.session_state["result"]
    st.subheader("Generated output")
    st.markdown(output)
    st.download_button("Download output", output, "low_resource_output.txt")
    checks = basic_output_checks(output)
    st.write("Output checks", checks)
    expected_script = LANGUAGES[language]["script"]
    ratio = script_match_ratio(output, expected_script)
    st.metric("Expected script character ratio", f"{ratio:.0%}")
    st.caption("Script ratio is a lightweight diagnostic, not a translation-quality score.")

with st.expander("Recent history"):
    for row in reversed(load_records("data/history.jsonl", 10)):
        st.markdown(f"**{row['language']} · {row['task']}**")
        st.write(row["source"])
        st.write(row["output"])
