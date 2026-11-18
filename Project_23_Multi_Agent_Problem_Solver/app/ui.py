import json
import streamlit as st
from app.agents import MultiAgentProblemSolver, AgentError

st.set_page_config(page_title="Multi-Agent Problem Solver", layout="wide")
st.title("Multi-Agent Problem Solver")
st.caption("Planner → Analyst → Critic → Coordinator, using a local LLM.")
task = st.text_area(
    "Describe the problem",
    "How can a small team reduce customer support response time without increasing headcount?",
    height=130
)
use_llm = st.toggle("Use local Ollama model", value=True)
if st.button("Solve problem", type="primary"):
    try:
        with st.spinner("Specialist agents are working..."):
            result = MultiAgentProblemSolver(use_llm=use_llm).solve(task)
        st.subheader("Final coordinated solution")
        st.markdown(result["agents"]["coordinator"])
        tabs = st.tabs(["Planner", "Analyst", "Critic"])
        for tab, key in zip(tabs, ["planner", "analyst", "critic"]):
            with tab:
                st.markdown(result["agents"][key])
        st.download_button(
            "Download full agent report",
            json.dumps(result, ensure_ascii=False, indent=2),
            file_name="multi_agent_report.json",
            mime="application/json"
        )
    except (AgentError, ValueError) as exc:
        st.error(str(exc))
st.info("Disable Ollama to try the built-in deterministic template workflow without downloading a model.")
