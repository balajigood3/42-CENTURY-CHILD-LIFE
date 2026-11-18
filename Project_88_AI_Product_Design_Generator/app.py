import json
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd
from product_design.generator import generate_product_concept, validate_concept
from product_design.exporter import export_markdown

st.set_page_config(page_title="AI Product Design Generator", layout="wide")
st.title("AI Product Design Generator")
st.caption("Product idea-ஐ personas, feature backlog, MVP scope, requirements மற்றும் roadmap ஆக மாற்றும் local-first tool.")

with st.form("product_form"):
    product_name = st.text_input("Product name", "LearnPath")
    problem = st.text_area("Problem statement",
        "Students need an education platform to discover courses, practice skills and track learning progress.",
        height=110)
    audience = st.text_input("Target audience", "College students and independent learners")
    platform = st.selectbox("Target platform", ["Web", "Mobile", "Web and Mobile", "Desktop"])
    constraints = st.text_area("Constraints (optional)", "Small MVP team; no paid API keys.")
    include_mvp = st.checkbox("Generate MVP scope", value=True)
    submitted = st.form_submit_button("Generate product concept", type="primary")

if submitted:
    try:
        concept = validate_concept(generate_product_concept(
            product_name, problem, audience, platform, constraints, include_mvp
        ))
        st.session_state["product_concept"] = concept
    except ValueError as exc:
        st.error(str(exc))

concept = st.session_state.get("product_concept")
if concept:
    st.success("Product concept generated.")
    st.subheader("Product vision")
    st.write(concept["product_vision"])
    st.write(f"Domain: **{concept['domain']}** · Platform: **{concept['platform']}**")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Personas")
        st.dataframe(pd.DataFrame(concept["personas"]), use_container_width=True)
        st.subheader("Feature backlog")
        st.dataframe(pd.DataFrame(concept["feature_backlog"]), use_container_width=True)
        st.subheader("MVP scope")
        for item in concept["mvp_scope"]:
            st.write("• " + item)
    with c2:
        st.subheader("Requirements")
        st.dataframe(pd.DataFrame(concept["requirements"]), use_container_width=True)
        st.subheader("Delivery roadmap")
        for phase in concept["delivery_roadmap"]:
            with st.expander(phase["phase"]):
                for item in phase["deliverables"]:
                    st.write("• " + item)
        st.subheader("Success metrics")
        st.dataframe(pd.DataFrame(concept["success_metrics"]), use_container_width=True)
    st.subheader("Risks and mitigations")
    st.dataframe(pd.DataFrame(concept["risks_and_mitigations"]), use_container_width=True)
    st.download_button("Download JSON", json.dumps(concept, ensure_ascii=False, indent=2),
                       file_name="product_concept.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "product_concept.md"
        export_markdown(concept, path)
        markdown = path.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", markdown,
                       file_name="product_concept.md", mime="text/markdown")
    st.caption("Generated concept is a starting draft. Validate with users and technical stakeholders.")
