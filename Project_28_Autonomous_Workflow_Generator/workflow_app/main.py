import json
import streamlit as st
from .generator import generate_workflow, to_mermaid

st.set_page_config(page_title="Autonomous Workflow Generator", page_icon="⚙️", layout="wide")
st.title("Autonomous Workflow Generator")
st.caption("Natural-language task → validated workflow plan and dependency graph")
st.warning("Planning tool only: generated actions are not executed. Review the plan before using it.")

task = st.text_area(
    "Describe the business task",
    placeholder="Example: Process a customer refund request from intake through approval and customer notification.",
    height=130
)
use_ollama = st.checkbox("Use local Ollama model when available", value=True)
if st.button("Generate workflow", type="primary", disabled=len(task.strip()) < 8):
    with st.spinner("Generating and validating workflow..."):
        try:
            workflow, status = generate_workflow(task, use_ollama=use_ollama)
            st.session_state["workflow_json"] = workflow.model_dump()
            st.session_state["workflow_status"] = status
        except Exception as exc:
            st.error(str(exc))

if "workflow_json" in st.session_state:
    data = st.session_state["workflow_json"]
    from workflow_app.schema import Workflow
    workflow = Workflow.model_validate(data)
    st.success(st.session_state["workflow_status"])
    st.subheader(workflow.title)
    st.write(workflow.objective)
    st.subheader("Execution order")
    for index, node in enumerate(workflow.topological_nodes(), 1):
        with st.expander(f"{index}. {node.name}", expanded=True):
            st.write(f"**Action:** {node.action}")
            st.write(f"**Owner:** {node.owner}")
            st.write(f"**Depends on:** {', '.join(node.depends_on) or 'None'}")
            st.write(f"**Inputs:** {', '.join(node.inputs) or 'None'}")
            st.write(f"**Outputs:** {', '.join(node.outputs) or 'None'}")
            st.write(f"**Failure handling:** {node.on_failure}")
    json_text = json.dumps(data, indent=2, ensure_ascii=False)
    mermaid_text = to_mermaid(workflow)
    left, right = st.columns(2)
    left.download_button("Download workflow JSON", json_text, "workflow.json", "application/json")
    right.download_button("Download Mermaid diagram", mermaid_text, "workflow.mmd", "text/plain")
    with st.expander("Raw JSON"):
        st.code(json_text, language="json")
    with st.expander("Mermaid source"):
        st.code(mermaid_text, language="mermaid")
