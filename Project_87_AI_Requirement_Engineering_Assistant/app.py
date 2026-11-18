import json
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd
from requirement_engineering.analyzer import analyze_requirements, validate_analysis
from requirement_engineering.exporter import export_markdown

st.set_page_config(page_title="AI Requirement Engineering Assistant", layout="wide")
st.title("AI Requirement Engineering Assistant")
st.caption("Requirement notes-ஐ functional / non-functional requirements, quality checks மற்றும் traceability matrix ஆக மாற்றும் local-first tool.")

sample = """The customer shall create an account using an email address.
The system must authenticate users before showing account information.
The dashboard should be fast and user-friendly.
The system shall export monthly reports.
Availability should be 99.9 percent each month."""
notes = st.text_area("Paste requirement notes", sample, height=240)
if st.button("Analyze requirements", type="primary"):
    try:
        st.session_state["requirements_result"] = validate_analysis(analyze_requirements(notes))
    except ValueError as exc:
        st.error(str(exc))

data = st.session_state.get("requirements_result")
if data:
    s = data["summary"]
    cols = st.columns(5)
    for col, label, value in zip(cols,
        ["Total", "Functional", "Non-functional", "Clarify", "Vague flags"],
        [s["total"], s["functional"], s["non_functional"], s["needs_clarification"], s["with_quality_flags"]]):
        col.metric(label, value)
    st.subheader("Requirement register")
    st.dataframe(pd.DataFrame(data["requirements"]), use_container_width=True)
    st.subheader("Clarification questions")
    for req in data["requirements"]:
        if req["clarification_questions"]:
            with st.expander(req["id"] + " — " + req["statement"]):
                for question in req["clarification_questions"]:
                    st.write("• " + question)
    st.subheader("Traceability matrix")
    st.dataframe(pd.DataFrame(data["traceability"]), use_container_width=True)
    st.download_button("Download JSON", json.dumps(data, ensure_ascii=False, indent=2),
                       file_name="requirements_analysis.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "requirements_report.md"
        export_markdown(data, path)
        report = path.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", report,
                       file_name="requirements_report.md", mime="text/markdown")
    st.caption(data["disclaimer"])
