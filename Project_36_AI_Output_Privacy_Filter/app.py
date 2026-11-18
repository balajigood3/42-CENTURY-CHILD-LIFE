import json
import streamlit as st
from privacy_filter.detector import filter_output

st.set_page_config(page_title="AI Output Privacy Filter", page_icon="🔒", layout="wide")
st.title("AI Output Privacy Filter")
st.caption("Inspect and protect generated text locally. No paid API keys or external model calls.")
text = st.text_area("Paste AI-generated output", height=260, placeholder="Example: Contact me at person@example.com")
mode = st.radio("Protection mode", ["redact", "block", "report"], horizontal=True,
                format_func=lambda x: {"redact":"Redact sensitive values","block":"Block if sensitive data exists","report":"Report only"}[x])
if st.button("Scan and protect", type="primary"):
    try:
        result = filter_output(text, mode)
        st.metric("Detected items", result["finding_count"])
        st.write("Status:", result["status"].replace("_", " ").upper())
        st.subheader("Protected output")
        st.text_area("Result", result["safe_output"], height=180)
        if result["findings"]:
            st.dataframe(result["findings"], use_container_width=True)
        else:
            st.success("No configured patterns detected.")
        st.download_button("Download JSON report", json.dumps(result, indent=2), "privacy-filter-report.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
