import json
import streamlit as st
from .scanner import scan_text

st.set_page_config(page_title="AI Data Leakage Prevention", page_icon="🔐", layout="wide")
st.title("AI Data Leakage Prevention")
st.caption("Detect and redact common personal data, identifiers, payment-card-like values, and credentials.")
st.warning("Local pattern scanner only. It does not transmit the text to an external service. It is not a complete DLP or compliance solution.")

text = st.text_area(
    "Paste text to scan",
    placeholder="Example: Contact user@example.com. API_KEY=example-secret-123456",
    height=180
)
if st.button("Scan and redact", type="primary", disabled=not text.strip()):
    report = scan_text(text)
    st.session_state["report"] = {
        "risk_score": report.risk_score,
        "risk_level": report.risk_level,
        "finding_count": report.finding_count,
        "findings": report.findings,
        "sanitized_text": report.sanitized_text,
        "recommendation": report.recommendation
    }

if "report" in st.session_state:
    report = st.session_state["report"]
    st.subheader("Leakage assessment")
    c1,c2,c3 = st.columns(3)
    c1.metric("Risk score", f'{report["risk_score"]}/100')
    c2.metric("Risk level", report["risk_level"])
    c3.metric("Findings", report["finding_count"])
    if report["risk_level"] == "High":
        st.error(report["recommendation"])
    elif report["risk_level"] != "None detected":
        st.warning(report["recommendation"])
    else:
        st.success(report["recommendation"])
    st.subheader("Detected data")
    if report["findings"]:
        safe_findings = [
            {"category": f["category"], "data_type": f["data_type"],
             "risk_points": f["risk_points"], "replacement": f["replacement"]}
            for f in report["findings"]
        ]
        st.dataframe(safe_findings, use_container_width=True, hide_index=True)
        st.caption("For privacy, the UI does not display the original matched values in the findings table.")
    else:
        st.info("No configured sensitive-data patterns matched.")
    st.subheader("Sanitized output")
    st.code(report["sanitized_text"])
    st.download_button("Download sanitized text", report["sanitized_text"], "sanitized_output.txt", "text/plain")
    st.download_button("Download scan report", json.dumps(report, indent=2), "dlp_report.json", "application/json")

st.caption("For production: add organization-specific detectors, secret vault integration, access controls, audit retention policies, and human review.")
