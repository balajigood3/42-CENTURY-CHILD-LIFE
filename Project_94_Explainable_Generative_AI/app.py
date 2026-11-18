import json
import streamlit as st
import pandas as pd
from xai_engine.explain import explain_text, compare_explanations, DEFAULT_WEIGHTS

st.set_page_config(page_title="Explainable Generative AI", layout="wide")
st.title("Explainable Generative AI")
st.caption("AI prediction-க்கு எந்த input features காரணமாக score மாறியது என்பதை வெளிப்படையாகக் காட்டும் XAI demonstration.")

st.info("This demo uses a transparent keyword-weight baseline. It does not claim to expose hidden reasoning from an LLM.")
text = st.text_area("Enter a message", "URGENT: invoice payment failed, please resolve ASAP.")
threshold = st.slider("Priority threshold", 0.0, 8.0, 1.5, 0.1)
if st.button("Explain prediction", type="primary"):
    try:
        result = explain_text(text, threshold=threshold)
        st.session_state.xai_result = result
    except ValueError as exc:
        st.error(str(exc))

if "xai_result" in st.session_state:
    result = st.session_state.xai_result
    c1, c2 = st.columns(2)
    c1.metric("Prediction", result["prediction"])
    c2.metric("Feature score", result["score"])
    st.subheader("Feature contributions")
    if result["feature_contributions"]:
        st.dataframe(pd.DataFrame(result["feature_contributions"]), use_container_width=True)
        st.bar_chart(pd.DataFrame(result["feature_contributions"]).set_index("feature")[["weight"]])
    else:
        st.write("No known weighted keywords were found.")
    st.subheader("Unmatched tokens")
    st.write(", ".join(result["unmatched_tokens"]) or "None")
    st.subheader("Threshold sensitivity")
    st.dataframe(pd.DataFrame(compare_explanations(text)), use_container_width=True)
    st.download_button("Download explanation JSON", json.dumps(result, indent=2),
                       file_name="explanation.json", mime="application/json")
    for note in result["limitations"]:
        st.caption("• " + note)

st.sidebar.subheader("Model feature weights")
st.sidebar.json(DEFAULT_WEIGHTS)
