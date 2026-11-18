import json
import streamlit as st
from knowledge_worker.worker import build_plan, execute_plan, ALLOWED_ACTIONS

st.set_page_config(page_title="Autonomous Knowledge Worker", layout="wide")
st.title("Autonomous Knowledge Worker")
st.caption("உங்கள் documents-இல் இருந்து bounded knowledge-work tasks-ஐ திட்டமிட்டு இயக்கும் local assistant.")

st.warning("Prototype mode: supplied text மட்டுமே பயன்படுத்தப்படும். Email, shell commands, network calls அல்லது வெளிப்புற actions எதுவும் செய்யப்படாது.")
goal = st.text_area("Knowledge-work goal", "Prepare a project status brief and identify pending actions.")
uploaded = st.file_uploader("Upload text or Markdown files", type=["txt", "md"], accept_multiple_files=True)
manual_title = st.text_input("Additional source title", "Notes")
manual_content = st.text_area("Additional source content", "The project review is scheduled for 20 November 2026. The team must complete testing and prepare the release checklist.")
actions = st.multiselect("Choose workflow actions", sorted(ALLOWED_ACTIONS),
                         default=["summarize", "extract", "checklist", "draft"])
if st.button("Plan and execute", type="primary"):
    docs = []
    for f in uploaded or []:
        docs.append({"title": f.name, "content": f.getvalue().decode("utf-8", errors="replace")})
    if manual_content.strip():
        docs.append({"title": manual_title or "Notes", "content": manual_content})
    try:
        plan = build_plan(goal, docs, actions)
        result = execute_plan(plan)
        st.session_state["worker_plan"] = plan
        st.session_state["worker_result"] = result
        st.success(f"Completed {result['completed_steps']} workflow steps.")
    except ValueError as exc:
        st.error(str(exc))

if "worker_plan" in st.session_state:
    st.subheader("Execution plan")
    st.json(st.session_state["worker_plan"])
    st.subheader("Results")
    st.json(st.session_state["worker_result"])
    payload = json.dumps({"plan": st.session_state["worker_plan"],
                          "result": st.session_state["worker_result"]},
                         ensure_ascii=False, indent=2)
    st.download_button("Download workflow report (JSON)", payload,
                       file_name="knowledge_worker_report.json", mime="application/json")
