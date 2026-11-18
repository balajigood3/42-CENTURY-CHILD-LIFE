import streamlit as st
from devops_assistant.analyzer import analyze_compose, create_plan
import json

st.set_page_config(page_title="Autonomous DevOps Assistant", layout="wide")
st.title("Autonomous DevOps Assistant")
st.caption("Static configuration review and artifact generation — no deployment or shell execution.")
sample = """services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
    privileged: true
"""
config = st.text_area("Docker Compose YAML", value=sample, height=260)
if st.button("Analyze configuration", type="primary"):
    try:
        report = analyze_compose(config)
        st.metric("Findings", report["finding_count"])
        st.json(report["severity_counts"])
        st.dataframe(report["findings"], use_container_width=True)
        st.download_button("Download risk_report.json", json.dumps(report, indent=2), "risk_report.json")
        st.download_button("Download DEPLOYMENT_PLAN.md", create_plan(report), "DEPLOYMENT_PLAN.md")
    except ValueError as exc:
        st.error(str(exc))
