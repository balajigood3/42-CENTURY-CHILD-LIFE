import json
import streamlit as st
from app.collaboration import CollaborationPlatform, CollaborationError

st.set_page_config(page_title="Agent Collaboration Platform", layout="wide")
st.title("Agent Collaboration Platform")
st.caption("A fixed multi-agent workflow: Planner → Researcher → Reviewer → Coordinator.")
task = st.text_area(
    "Team task or problem",
    "Design a low-cost employee onboarding process for a 30-person startup.",
    height=130
)
use_llm = st.toggle("Use local Ollama model", value=True)
if st.button("Start collaboration", type="primary"):
    try:
        with st.spinner("Agents are collaborating..."):
            result = CollaborationPlatform(use_llm=use_llm).collaborate(task)
        st.subheader("Final coordinated outcome")
        st.markdown(result["final_outcome"])
        tabs = st.tabs(["Planner", "Researcher", "Reviewer", "Coordinator"])
        for tab, item in zip(tabs, result["messages"]):
            with tab:
                st.markdown(item["message"])
        st.download_button(
            "Download collaboration report",
            json.dumps(result, ensure_ascii=False, indent=2),
            file_name="agent_collaboration_report.json",
            mime="application/json"
        )
    except (CollaborationError, ValueError) as exc:
        st.error(str(exc))
st.info("Offline mode uses deterministic templates. LLM mode sends each agent's previous messages as context to one local Ollama model.")
