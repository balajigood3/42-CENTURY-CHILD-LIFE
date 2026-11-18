import json
import streamlit as st
from business_process.generator import generate_process, validate_process
from business_process.exporter import export_json, export_markdown

st.set_page_config(page_title="AI Business Process Generator", layout="wide")
st.title("AI Business Process Generator")
st.caption("இயல்பான மொழியில் உள்ள business workflow விளக்கத்தை process blueprint, controls, KPIs மற்றும் flowchart ஆக மாற்றுங்கள்.")
with st.form("generator"):
    name = st.text_input("Process name", "Customer onboarding")
    objective = st.text_input("Business objective", "Onboard customers accurately and efficiently")
    description = st.text_area("Describe the current or desired process",
        "Customer submits an onboarding request. Sales checks the details, operations verifies documents, manager approves exceptions, and the system activates the account.",
        height=150)
    controls = st.checkbox("Include risks and controls", value=True)
    submitted = st.form_submit_button("Generate process")
if submitted:
    try:
        result = validate_process(generate_process(description, name, objective, controls))
        st.session_state["process_result"] = result
    except ValueError as exc:
        st.error(str(exc))

result = st.session_state.get("process_result")
if result:
    st.success("Process blueprint generated.")
    st.subheader(result["process_name"])
    st.write(result["objective"])
    st.markdown("### Workflow steps")
    st.dataframe(result["steps"], use_container_width=True)
    st.markdown("### Flowchart")
    st.code(result["mermaid_flowchart"], language="mermaid")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Risks and controls")
        st.dataframe(result["risks_and_controls"], use_container_width=True)
    with col2:
        st.markdown("### KPIs")
        st.dataframe(result["kpis"], use_container_width=True)
    st.markdown("### Stakeholders and assumptions")
    st.write(result["stakeholders"])
    for item in result["assumptions"]:
        st.caption("• " + item)
    st.download_button("Download JSON", json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="business_process.json", mime="application/json")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        md_path = f"{tmp}/process.md"
        export_markdown(result, md_path)
        with open(md_path, encoding="utf-8") as handle:
            md_content = handle.read()
    st.download_button("Download Markdown report", md_content,
                       file_name="business_process.md", mime="text/markdown")
