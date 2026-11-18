import json
import tempfile
from pathlib import Path
import streamlit as st
from meeting_intelligence.analyzer import analyze_transcript, validate_analysis
from meeting_intelligence.exporter import export_markdown

st.set_page_config(page_title="AI Meeting Intelligence System", layout="wide")
st.title("AI Meeting Intelligence System")
st.caption("Meeting transcript-இலிருந்து summary, decisions, action items மற்றும் blockers உருவாக்கும் local-first tool.")

with st.form("meeting_form"):
    title = st.text_input("Meeting title", "Weekly Project Review")
    meeting_date = st.text_input("Meeting date (optional)", "2026-11-18")
    transcript = st.text_area("Paste transcript or meeting notes", height=260,
        placeholder="Example: Priya will prepare the API test report by Friday. We decided to freeze the release scope. Risk: vendor access may delay testing.")
    submitted = st.form_submit_button("Analyze meeting", type="primary")
if submitted:
    try:
        result = validate_analysis(analyze_transcript(transcript, title, meeting_date))
        st.session_state["meeting_result"] = result
    except ValueError as exc:
        st.error(str(exc))

result = st.session_state.get("meeting_result")
if result:
    st.success("Meeting analysis generated.")
    st.subheader("Summary")
    for item in result["summary"]:
        st.write("• " + item)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Decisions")
        for item in result["decisions"]:
            st.write("• " + item)
        st.subheader("Risks and blockers")
        for item in result["risks_and_blockers"]:
            st.warning(item)
    with col2:
        st.subheader("Action items")
        if result["action_items"]:
            st.dataframe(result["action_items"], use_container_width=True)
        else:
            st.info("No owner-task patterns detected.")
        st.subheader("Key topics")
        st.write(", ".join(result["key_topics"]))
    st.subheader("Follow-up questions")
    for item in result["follow_up_questions"]:
        st.write("• " + item)
    st.download_button("Download JSON", json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="meeting_analysis.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        report_path = Path(tmp) / "meeting_report.md"
        export_markdown(result, report_path)
        report = report_path.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", report,
                       file_name="meeting_report.md", mime="text/markdown")
    st.caption(result["disclaimer"])
