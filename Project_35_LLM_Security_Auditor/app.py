import json
import streamlit as st
from security_auditor.auditor import audit_text

st.set_page_config(page_title="LLM Security Auditor", page_icon="🔐", layout="wide")
st.title("LLM Security Auditor")
st.caption("Static, deterministic configuration checks — no paid API and no config execution.")
sample = open("samples/insecure_config.json", encoding="utf-8").read()
uploaded = st.file_uploader("Upload JSON/YAML configuration", type=["json", "yaml", "yml"])
default_text = uploaded.getvalue().decode("utf-8") if uploaded else sample
raw = st.text_area("Or paste configuration", value=default_text, height=300)
filename = uploaded.name if uploaded else "config.json"
if st.button("Run security audit", type="primary"):
    try:
        report = audit_text(raw, filename)
        st.metric("Risk score", f"{report['risk_score']}/100")
        st.write("Risk level:", report["risk_level"].upper())
        st.write("Findings:", report["finding_count"])
        if report["findings"]:
            st.dataframe(report["findings"], use_container_width=True)
        else:
            st.success("No configured checks triggered.")
        st.download_button("Download JSON report", json.dumps(report, indent=2), "security-audit.json", "application/json")
        md = ["# LLM Security Audit", f"- Risk score: {report['risk_score']}/100", f"- Risk level: {report['risk_level']}", ""]
        for item in report["findings"]:
            md += [f"## [{item['severity'].upper()}] {item['category']}", f"- Evidence: `{item['evidence']}`", f"- Finding: {item['explanation']}", f"- Fix: {item['remediation']}", ""]
        md.append(report["disclaimer"])
        st.download_button("Download Markdown report", "\n".join(md), "security-audit.md", "text/markdown")
    except Exception as exc:
        st.error(f"Could not audit configuration: {exc}")
