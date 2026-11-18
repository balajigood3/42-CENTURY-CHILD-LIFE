import json
import streamlit as st
from document_guard.scanner import scan_text

st.set_page_config(page_title="Untrusted Document Detection AI", page_icon="📄", layout="wide")
st.title("Untrusted Document Detection AI")
st.caption("Inspect documents for instruction-like and potentially malicious content before RAG ingestion.")
uploaded = st.file_uploader("Upload text document", type=["txt", "md", "csv", "json", "yaml", "yml", "xml", "html"])
default = uploaded.getvalue().decode("utf-8", errors="replace") if uploaded else ""
text = st.text_area("Or paste document content", value=default, height=300)
source = uploaded.name if uploaded else "pasted_text"
if st.button("Scan document", type="primary"):
    try:
        report = scan_text(text, source)
        a, b = st.columns(2)
        a.metric("Risk score", f"{report['risk_score']}/100")
        b.metric("Findings", report["finding_count"])
        st.write("Risk level:", report["risk_level"].upper())
        st.write("Recommended action:", report["recommended_action"])
        if report["findings"]:
            st.dataframe(report["findings"], use_container_width=True)
        else:
            st.success("No configured risk patterns detected.")
        st.download_button("Download scan report", json.dumps(report, indent=2), "document-scan-report.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
