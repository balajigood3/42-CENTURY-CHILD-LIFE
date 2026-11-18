import json
import streamlit as st
import pandas as pd
from bias_audit.audit import audit_fairness, mitigation_experiments

st.set_page_config(page_title="AI Bias Detection & Mitigation", layout="wide")
st.title("AI Bias Detection & Mitigation")
st.caption("Classification results-இல் group-wise disparities-ஐ ஆய்வு செய்து, பாதுகாப்பான mitigation experiments-ஐ பரிந்துரைக்கும் fairness audit tool.")

st.warning("Use only lawfully collected, appropriately governed audit data. This tool does not infer sensitive attributes or change model predictions.")
uploaded = st.file_uploader("Upload CSV audit data", type=["csv"])
st.write("Required columns: group, actual, predicted. Both actual and predicted must be 0 or 1.")
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.dataframe(df.head(20), use_container_width=True)
        group_col = st.selectbox("Group column", list(df.columns), index=list(df.columns).index("group") if "group" in df.columns else 0)
        actual_col = st.selectbox("Actual label column", list(df.columns), index=list(df.columns).index("actual") if "actual" in df.columns else 0)
        pred_col = st.selectbox("Predicted label column", list(df.columns), index=list(df.columns).index("predicted") if "predicted" in df.columns else 0)
        if st.button("Run fairness audit", type="primary"):
            rows = df.to_dict(orient="records")
            result = mitigation_experiments(rows, group_col, actual_col, pred_col)
            st.session_state.bias_result = result
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")

if "bias_result" in st.session_state:
    result = st.session_state.bias_result
    audit = result["audit"]
    st.subheader("Group-wise metrics")
    st.dataframe(pd.DataFrame(audit["group_metrics"]).T, use_container_width=True)
    st.subheader("Disparity gaps")
    st.json(audit["disparity_gaps"])
    if audit["flags"]:
        for flag in audit["flags"]:
            st.warning(flag)
    else:
        st.success("No configured disparity-gap flag was triggered. This does not prove fairness.")
    st.subheader("Suggested mitigation experiments")
    for item in result["mitigation_experiments"]:
        st.write("• " + item)
    st.download_button("Download audit report", json.dumps(result, indent=2),
                       file_name="fairness_audit.json", mime="application/json")
    for caveat in audit["caveats"]:
        st.caption("• " + caveat)
