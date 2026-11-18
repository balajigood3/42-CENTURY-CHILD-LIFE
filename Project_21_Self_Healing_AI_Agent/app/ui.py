import streamlit as st
from app.agent import SelfHealingAgent

st.set_page_config(page_title="Self-Healing AI Agent", page_icon="🛠️", layout="wide")
st.title("Self-Healing AI Agent")
st.caption("Bounded plan → execute → observe → retry workflow. Local tools only.")
task = st.text_area("Task", "calculate 12 * 4", height=100)
max_attempts = st.slider("Maximum attempts per step", 1, 5, 2)
use_llm = st.toggle("Use local Ollama planner", value=True)
if st.button("Run agent", type="primary"):
    agent = SelfHealingAgent(workspace="workspace", max_attempts=max_attempts, use_llm=use_llm)
    result = agent.run(task)
    st.subheader("Result")
    st.write(result["message"])
    for item in result.get("results", []):
        st.code(item)
    st.subheader("Execution log")
    st.json(result.get("logs", []))
st.info("Example tasks: `calculate 12 * 4`, `uppercase: hello world`, `count words: local agent demo`")
