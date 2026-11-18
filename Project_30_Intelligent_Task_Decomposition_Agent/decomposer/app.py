import json
import streamlit as st
from .engine import decompose_task, to_mermaid

st.set_page_config(page_title="Intelligent Task Decomposition Agent", page_icon="🧩", layout="wide")
st.title("Intelligent Task Decomposition Agent")
st.caption("Complex task → actionable subtasks → dependency graph → execution order")
st.warning("Planning assistant only. It does not execute tasks or run generated commands.")

task = st.text_area("Enter a complex task or project description",
    placeholder="Example: Build and deploy a secure document Q&A application with upload, retrieval, evaluation, and monitoring.",
    height=140)
use_ollama = st.checkbox("Use local Ollama model when available", value=True)

if st.button("Decompose task", type="primary", disabled=len(task.strip()) < 8):
    with st.spinner("Decomposing and validating tasks..."):
        try:
            result, status = decompose_task(task, use_ollama)
            st.session_state["breakdown"] = result.model_dump()
            st.session_state["status"] = status
        except Exception as exc:
            st.error(str(exc))

if "breakdown" in st.session_state:
    from .models import TaskBreakdown
    result = TaskBreakdown.model_validate(st.session_state["breakdown"])
    st.success(st.session_state["status"])
    st.subheader(result.project)
    st.write(result.objective)
    a,b = st.columns(2)
    a.metric("Subtasks", len(result.subtasks))
    b.metric("Estimated effort", f"{result.total_estimated_hours} hours")
    st.subheader("Execution order")
    for index, item in enumerate(result.execution_order(), 1):
        with st.expander(f'{index}. {item.id} · {item.title}', expanded=True):
            st.write(item.description)
            st.write(f"**Priority:** {item.priority}")
            st.write(f"**Estimated effort:** {item.estimated_hours} hours")
            st.write(f"**Dependencies:** {', '.join(item.depends_on) or 'None'}")
            st.write(f"**Deliverable:** {item.deliverable}")
            st.write(f"**Acceptance criteria:** {item.acceptance_criteria}")
    json_data = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
    mermaid = to_mermaid(result)
    c1,c2 = st.columns(2)
    c1.download_button("Download task breakdown JSON", json_data, "task_breakdown.json", "application/json")
    c2.download_button("Download dependency diagram", mermaid, "task_dependencies.mmd", "text/plain")
    with st.expander("Raw JSON"):
        st.code(json_data, language="json")
    with st.expander("Mermaid diagram source"):
        st.code(mermaid, language="mermaid")
