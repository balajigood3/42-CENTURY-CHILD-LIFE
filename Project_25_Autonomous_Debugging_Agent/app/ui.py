import streamlit as st
from app.debugger import debug_source, DebuggerError

st.set_page_config(page_title="Autonomous Debugging Agent", layout="wide")
st.title("Autonomous Debugging Agent")
st.caption("Analyze Python source + traceback and propose a syntax-checked correction using local Ollama.")
source = st.text_area(
    "Python source code",
    "def divide(a, b):\n    return a / b\n\nprint(divide(10, 0))",
    height=240
)
error_log = st.text_area(
    "Error log / traceback",
    "Traceback (most recent call last):\n  File \"main.py\", line 4, in <module>\n    print(divide(10, 0))\nZeroDivisionError: division by zero",
    height=150
)
use_llm = st.toggle("Use local Ollama model", value=True)
if st.button("Analyze and propose fix", type="primary"):
    try:
        with st.spinner("Analyzing source and traceback..."):
            result = debug_source(source, error_log, use_llm=use_llm)
        st.subheader("Diagnosis")
        st.markdown(result["analysis"])
        st.subheader("Syntax validation")
        st.write(result["validation"])
        st.write("Proposed code syntax valid:", result["syntax_valid"])
        if result["proposed_code"]:
            st.subheader("Proposed corrected code")
            st.code(result["proposed_code"], language="python")
            st.download_button("Download proposed Python file", result["proposed_code"],
                               file_name="proposed_fix.py", mime="text/x-python")
        if result["diff"]:
            with st.expander("Review unified diff"):
                st.code(result["diff"], language="diff")
    except DebuggerError as exc:
        st.error(str(exc))
st.warning("The agent never executes supplied or generated code. Review proposed changes and run tests in your own isolated environment.")
