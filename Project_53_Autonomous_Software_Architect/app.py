import streamlit as st
from architect.engine import create_architecture, bundle_zip

st.set_page_config(page_title="Autonomous Software Architect", layout="wide")
st.title("Autonomous Software Architect")
st.caption("Turn a software brief into a structured architecture pack. Deterministic, local, and free of paid API keys.")

with st.form("brief"):
    name = st.text_input("Project name", "Clinic Appointment Platform")
    brief = st.text_area("Problem statement / requirements", "Build a web platform for patients to book clinic appointments. Staff manage schedules and administrators manage users and reports.")
    scale = st.selectbox("Expected scale", ["small", "medium", "large"])
    data_sensitivity = st.selectbox("Data sensitivity", ["public", "internal", "sensitive"])
    availability = st.selectbox("Availability target", ["standard", "high"])
    submitted = st.form_submit_button("Design architecture", type="primary")

if submitted:
    try:
        result = create_architecture(name, brief, scale, data_sensitivity, availability)
        st.session_state["architecture"] = result
        st.session_state["archive"] = bundle_zip(result)
    except ValueError as exc:
        st.error(str(exc))

if "architecture" in st.session_state:
    result = st.session_state["architecture"]
    st.success("Architecture pack generated.")
    tabs = st.tabs(["Overview", "Architecture diagram", "Requirements", "Security", "Deployment", "All files"])
    with tabs[0]:
        st.markdown(result["ARCHITECTURE.md"])
    with tabs[1]:
        st.code(result["architecture.mmd"], language="mermaid")
    with tabs[2]:
        st.markdown(result["requirements.md"])
    with tabs[3]:
        st.markdown(result["security-review.md"])
    with tabs[4]:
        st.markdown(result["deployment-plan.md"])
    with tabs[5]:
        selected = st.selectbox("Select file", sorted(result))
        st.code(result[selected])
    st.download_button("Download architecture pack ZIP", st.session_state["archive"],
                       file_name="software_architecture_pack.zip", mime="application/zip")
