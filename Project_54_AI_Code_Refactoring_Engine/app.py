import streamlit as st
from refactor_engine.engine import analyze_and_refactor, make_zip

st.set_page_config(page_title="AI Code Refactoring Engine", layout="wide")
st.title("AI Code Refactoring Engine")
st.caption("Static, deterministic refactoring suggestions for Python source. No paid API keys.")

uploaded = st.file_uploader("Upload a Python file", type=["py"])
source = st.text_area("Or paste Python code", height=320, placeholder="def calculate_total(items):\n    total = 0\n    for item in items:\n        total = total + item\n    return total")
apply_safe = st.checkbox("Apply safe automated transformations", value=True)

if st.button("Analyze and refactor", type="primary"):
    code = uploaded.getvalue().decode("utf-8") if uploaded else source
    try:
        result = analyze_and_refactor(code, apply_safe=apply_safe)
        st.session_state["result"] = result
        st.session_state["zip"] = make_zip(result)
    except (ValueError, UnicodeDecodeError) as exc:
        st.error(str(exc))

if "result" in st.session_state:
    result = st.session_state["result"]
    st.subheader("Analysis")
    st.metric("Findings", len(result["findings"]))
    if result["findings"]:
        for finding in result["findings"]:
            st.markdown(f"- **{finding['severity']} — {finding['rule']}** (line {finding['line']}): {finding['message']}")
    else:
        st.success("No supported issues detected.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Original source**")
        st.code(result["original"], language="python")
    with right:
        st.markdown("**Refactored source**")
        st.code(result["refactored"], language="python")
    st.download_button("Download refactoring report ZIP", st.session_state["zip"],
                       file_name="code_refactoring_report.zip", mime="application/zip")
