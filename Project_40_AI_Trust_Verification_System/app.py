import json
import streamlit as st
from trust_verifier.verifier import assess_claim

st.set_page_config(page_title="AI Trust Verification System", page_icon="🔎", layout="wide")
st.title("AI Trust Verification System")
st.caption("Assess claim wording and source metadata using a local reference list. No paid API or web fetching.")
claim = st.text_area("Claim to assess", "NIST publishes cybersecurity guidance.")
sources_raw = st.text_area("Sources (JSON array)", json.dumps([
    {"title": "NIST", "publisher": "National Institute of Standards and Technology", "url": "https://www.nist.gov/"}
], indent=2), height=180)
if st.button("Assess trust signals", type="primary"):
    try:
        sources = json.loads(sources_raw)
        if not isinstance(sources, list):
            raise ValueError("Sources must be a JSON array.")
        report = assess_claim(claim, sources)
        a, b = st.columns(2)
        a.metric("Risk score", f"{report['risk_score']}/100")
        b.metric("Sources", report["source_count"])
        st.write("Assessment:", report["assessment"].replace("_", " ").upper())
        if report["claim_flags"]:
            st.warning("Claim wording flags: " + ", ".join(report["claim_flags"]))
        st.subheader("Source assessments")
        st.dataframe(report["sources"], use_container_width=True)
        st.download_button("Download verification report", json.dumps(report, indent=2), "trust-verification-report.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
