import json
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd
from decision_intelligence.engine import analyze_decision, sensitivity_analysis
from decision_intelligence.exporter import export_markdown

st.set_page_config(page_title="AI Business Decision Intelligence", layout="wide")
st.title("AI Business Decision Intelligence")
st.caption("வணிகத் தேர்வுகளை weighted criteria அடிப்படையில் ஒப்பிட்டு, ranking மற்றும் sensitivity analysis உருவாக்கும் decision-support tool.")

st.info("Example: Compare CRM vendors, cloud platforms, project proposals or investment alternatives. Enter scores from 0 (poor) to 10 (excellent).")
with st.form("decision_form"):
    option_names = st.text_input("Options (comma-separated)", "Vendor A, Vendor B, Vendor C")
    criterion_names = st.text_input("Criteria (comma-separated)", "Cost, Reliability, Support, Scalability")
    st.markdown("**Criterion weights** (relative importance)")
    criteria = [x.strip() for x in criterion_names.split(",") if x.strip()]
    weights = {}
    directions = {}
    for criterion in criteria:
        c1, c2 = st.columns(2)
        weights[criterion] = c1.number_input(f"{criterion} weight", min_value=0.0, value=1.0, step=0.5, key=f"w_{criterion}")
        directions[criterion] = c2.selectbox(f"{criterion} direction", ["benefit", "cost"], key=f"d_{criterion}")
    st.markdown("**Option scores**")
    names = [x.strip() for x in option_names.split(",") if x.strip()]
    score_inputs = {}
    for name in names:
        st.markdown(f"_{name}_")
        score_inputs[name] = {}
        cols = st.columns(max(1, len(criteria)))
        for i, criterion in enumerate(criteria):
            score_inputs[name][criterion] = cols[i].number_input(
                f"{criterion} score for {name}", min_value=0.0, max_value=10.0,
                value=7.0, step=0.5, key=f"s_{name}_{criterion}"
            )
    submitted = st.form_submit_button("Analyze decision", type="primary")

if submitted:
    try:
        options = [{"name": name, "scores": scores} for name, scores in score_inputs.items()]
        result = analyze_decision(options, weights, directions)
        sensitivity = sensitivity_analysis(options, weights, directions)
        st.session_state["decision_result"] = result
        st.session_state["sensitivity_result"] = sensitivity
    except ValueError as exc:
        st.error(str(exc))

result = st.session_state.get("decision_result")
if result:
    st.success(f"Highest weighted score: {result['recommended_option']}")
    st.metric("Score gap to runner-up", result["score_gap_to_runner_up"])
    st.subheader("Option ranking")
    st.dataframe(pd.DataFrame(result["ranking"]), use_container_width=True)
    st.bar_chart(pd.DataFrame(result["ranking"]).set_index("name")[["total_score"]])
    st.subheader("Normalized weights")
    st.dataframe(pd.DataFrame([{"criterion": k, "weight": v,
                                "direction": result["criterion_directions"][k]}
                               for k, v in result["normalized_weights"].items()]),
                 use_container_width=True)
    st.subheader("Sensitivity analysis")
    sens = st.session_state["sensitivity_result"]
    st.write("Base recommendation:", sens["base_recommendation"])
    st.dataframe(pd.DataFrame(sens["scenarios"]), use_container_width=True)
                 if sens["scenarios"] else pd.DataFrame())
    st.download_button("Download JSON", json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="decision_analysis.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "decision_report.md"
        export_markdown(result, path)
        report = path.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", report,
                       file_name="decision_report.md", mime="text/markdown")
    for caveat in result["caveats"]:
        st.caption("• " + caveat)
