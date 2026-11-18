import streamlit as st
from code_agent import analyze_source, apply_safe_fixes, build_report

st.set_page_config(page_title="Self-Healing Code Agent", page_icon="🛠️", layout="wide")
st.title("Self-Healing Code Agent")
st.caption("Analyze Python source and error logs, suggest safe fixes, and validate syntax without executing uploaded code.")

uploaded = st.file_uploader("Upload Python source", type=["py"])
source_default = """def greet(name=None):
    if name == None:
        return "Hello"
    return "Hello " + name

try:
    greet()
except:
    print("failed")
"""
source = st.text_area("Python source code", value=source_default, height=300)
logs = st.text_area("Error logs / traceback (optional)", height=140,
                    placeholder="Paste the traceback or test failure output…")

col1, col2 = st.columns(2)
with col1:
    analyze_clicked = st.button("Analyze code", type="primary")
with col2:
    repair_clicked = st.button("Apply safe fixes")

if uploaded is not None and not source.strip():
    source = uploaded.getvalue().decode("utf-8", errors="replace")

if analyze_clicked or repair_clicked:
    try:
        if not source.strip():
            raise ValueError("Provide Python source code or upload a .py file.")
        report = analyze_source(source, logs)
        st.session_state["analysis_report"] = report
        if repair_clicked:
            repaired, changes = apply_safe_fixes(source)
            st.session_state["repaired_source"] = repaired
            st.session_state["safe_changes"] = changes
    except Exception as exc:
        st.error(str(exc))

if "analysis_report" in st.session_state:
    report = st.session_state["analysis_report"]
    st.subheader("Analysis report")
    st.write(f"**Syntax valid:** {'Yes' if report['syntax_valid'] else 'No'}")
    st.write(f"**Issues detected:** {len(report['issues'])}")
    for issue in report["issues"]:
        st.warning(f"{issue['severity']} · {issue['line']} · {issue['message']}")
    if report["log_hints"]:
        st.markdown("### Error-log hints")
        for hint in report["log_hints"]:
            st.write(f"- {hint}")
    st.download_button("Download analysis JSON", build_report(report),
                       file_name="code_analysis.json", mime="application/json")

if "repaired_source" in st.session_state:
    st.subheader("Safe-fix result")
    if st.session_state["safe_changes"]:
        for change in st.session_state["safe_changes"]:
            st.write(f"- {change}")
    else:
        st.info("No supported automatic safe fixes were found.")
    st.code(st.session_state["repaired_source"], language="python")
    st.download_button("Download repaired source", st.session_state["repaired_source"],
                       file_name="repaired_code.py", mime="text/x-python")
