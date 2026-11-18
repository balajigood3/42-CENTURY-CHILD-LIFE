import json
import streamlit as st
from evolving_ai.architecture import (
    COMPONENTS, propose_architecture, evaluate_architecture, propose_evolution
)

st.set_page_config(page_title="Self-Evolving AI Architecture", layout="wide")
st.title("Self-Evolving AI Architecture")
st.caption("Evaluation signals அடிப்படையில் architecture மாற்றங்களை முன்மொழியும்; தானாக production system-ஐ மாற்றாது.")

st.warning("Safety boundary: this prototype creates architecture proposals only. It never edits source code, deploys changes, or modifies a live system.")
with st.form("architecture"):
    goal = st.text_area("System goal", "Build a reliable internal knowledge assistant.")
    needs = st.multiselect("Required capabilities", list(COMPONENTS),
                           default=["retrieval", "memory", "planner", "human_review", "monitoring"])
    budget = st.number_input("Architecture cost budget (abstract units)", min_value=1, max_value=30, value=15)
    create = st.form_submit_button("Generate architecture proposal", type="primary")
if create:
    try:
        st.session_state.architecture = propose_architecture(
            {"goal": goal, "needs": needs, "budget": int(budget)})
        st.success("Architecture proposal created.")
    except ValueError as exc:
        st.error(str(exc))

architecture = st.session_state.get("architecture")
if architecture:
    st.subheader("Architecture proposal")
    st.metric("Estimated cost", architecture["estimated_cost"])
    st.metric("Capability score", architecture["capability_score"])
    st.dataframe(architecture["components"], use_container_width=True)
    st.json(architecture)
    st.subheader("Evaluate proposal")
    test_count = st.number_input("Number of evaluation checks", min_value=1, max_value=10, value=3)
    results = []
    for i in range(int(test_count)):
        c1, c2 = st.columns([3, 1])
        name = c1.text_input(f"Test {i+1} name", f"quality_check_{i+1}", key=f"tn{i}")
        passed = c2.checkbox("Passed", value=True, key=f"tp{i}")
        results.append({"name": name, "passed": passed})
    if st.button("Evaluate and propose evolution"):
        try:
            evaluation = evaluate_architecture(architecture, results)
            evolution = propose_evolution(architecture, evaluation)
            st.session_state.evaluation = evaluation
            st.session_state.evolution = evolution
        except ValueError as exc:
            st.error(str(exc))
    if "evaluation" in st.session_state:
        st.subheader("Evaluation")
        st.json(st.session_state.evaluation)
        st.subheader("Evolution proposal")
        st.json(st.session_state.evolution)
        bundle = {"architecture": architecture,
                  "evaluation": st.session_state.evaluation,
                  "evolution_proposal": st.session_state.evolution}
        st.download_button("Download architecture review JSON",
                           json.dumps(bundle, ensure_ascii=False, indent=2),
                           file_name="architecture_review.json", mime="application/json")
