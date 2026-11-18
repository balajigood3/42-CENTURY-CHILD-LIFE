import json
import streamlit as st
from permission_agent.policy import principal_from_role, ROLE_DEFAULTS
from permission_agent.agent import run_agent, available_tools

st.set_page_config(page_title="AI Permission-Aware Agent", page_icon="🛡️", layout="wide")
st.title("AI Permission-Aware Agent")
st.caption("Role- and scope-based demo agent. All tools are local simulations; no external actions occur.")
role = st.selectbox("User role", list(ROLE_DEFAULTS.keys()))
user_id = st.text_input("Demo user ID", "user-001")
principal = principal_from_role(user_id, role)
st.write("Granted scopes:", ", ".join(principal.scopes))
st.subheader("Available tool permissions")
st.dataframe(available_tools(principal), use_container_width=True)

tool = st.selectbox("Requested tool", ["search_docs", "analyze_report", "create_draft", "manage_users"])
query = st.text_area("Task / query", "Explain the access policy")
approved = st.checkbox("Human approval granted (demo only)", value=False)
if st.button("Run permission check", type="primary"):
    try:
        result = run_agent(principal, tool, query, approved)
        if result["status"] == "completed":
            st.success("Authorized")
            st.text(result["result"])
        else:
            st.warning("Approval required before this action can proceed.")
        st.json(result["audit"])
        st.download_button("Download audit record", json.dumps(result, indent=2), "agent-audit.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
