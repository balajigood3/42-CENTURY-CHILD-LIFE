
import streamlit as st
from testgen.engine import generate_tests, make_zip

st.set_page_config(page_title="Intelligent Test Case Generator", layout="wide")
st.title("Intelligent Test Case Generator")
st.caption("AST-based pytest test skeleton generator. No paid API keys.")
uploaded = st.file_uploader("Upload Python source", type=["py"])
source = st.text_area("Or paste Python code", height=300,
                      placeholder="def add(a: int, b: int) -> int:\n    return a + b")
include_edge = st.checkbox("Include boundary cases", value=True)
if st.button("Generate test cases", type="primary"):
    code = uploaded.getvalue().decode("utf-8") if uploaded else source
    try:
        result = generate_tests(code, include_edge)
        st.session_state["result"] = result
        st.session_state["archive"] = make_zip(result)
    except (ValueError, UnicodeDecodeError) as exc:
        st.error(str(exc))
if "result" in st.session_state:
    result = st.session_state["result"]
    st.metric("Functions analyzed", result["function_count"])
    st.metric("Test cases proposed", len(result["cases"]))
    st.code(result["test_code"], language="python")
    for case in result["cases"]:
        st.markdown(f"- **{case['function']} — {case['category']}**: {case['description']}")
    st.download_button("Download test package ZIP", st.session_state["archive"],
                       file_name="generated_test_cases.zip", mime="application/zip")
