import streamlit as st
from hypothesis_ai.generator import offline_template, to_markdown
from hypothesis_ai.llm import generate_hypotheses
from hypothesis_ai.history import save_generation, load_generations

st.set_page_config(page_title="AI Scientific Hypothesis Generator", layout="wide")
st.title("AI Scientific Hypothesis Generator")
st.caption("ஆராய்ச்சி observation மற்றும் background evidence அடிப்படையில் சோதிக்கக்கூடிய hypothesis-களை உருவாக்க உதவும் கருவி.")

with st.form("hypothesis_form"):
    field = st.text_input("Research field", placeholder="e.g. Environmental science")
    observation = st.text_area("Observation / phenomenon", placeholder="Describe the phenomenon you want to investigate.")
    background = st.text_area("Background evidence / literature notes", height=220,
                              placeholder="Paste relevant findings, summaries, or notes. Add source IDs if available.")
    study_type = st.selectbox("Preferred study type", [
        "Experimental", "Observational", "Computational", "Survey", "Mixed methods"])
    constraints = st.text_area("Constraints (optional)", placeholder="Population, available data, timeframe, resources...")
    model = st.text_input("Ollama model", "qwen2.5:3b")
    mode = st.radio("Mode", ["Local Ollama AI", "Offline template"], horizontal=True)
    submitted = st.form_submit_button("Generate hypotheses", type="primary")

if submitted:
    try:
        result = (generate_hypotheses(field, observation, background, study_type,
                                      constraints, model=model)
                  if mode == "Local Ollama AI"
                  else offline_template(field, observation, background))
        st.session_state["hypothesis_result"] = result
        save_generation("data/hypotheses.jsonl", field, observation, result)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

if st.session_state.get("hypothesis_result"):
    result = st.session_state["hypothesis_result"]
    st.subheader(result["field"])
    st.write(result["phenomenon"])
    st.markdown("### Background summary")
    st.write(result["background_summary"])
    st.markdown("### Candidate hypotheses")
    for i, h in enumerate(result["hypotheses"], 1):
        with st.expander(f"Hypothesis {i} · {h['confidence']} confidence", expanded=True):
            st.write(h["statement"])
            st.write("**Null hypothesis:** " + h["null_hypothesis"])
            st.write("**Rationale:** " + h["rationale"])
            st.write("**Study design:** " + h["study_design"])
            st.write("**Measurement:** " + h["measurement"])
            st.write("**Variables**")
            for key, values in h["variables"].items():
                st.write(f"{key.title()}: {', '.join(values)}")
            for key in ("predictions", "confounders", "ethical_considerations"):
                st.markdown(f"**{key.replace('_', ' ').title()}**")
                for value in h[key]:
                    st.markdown(f"- {value}")
    st.markdown("### Validation plan")
    for item in result["validation_plan"]:
        st.markdown(f"- {item}")
    st.markdown("### Limitations")
    for item in result["limitations"]:
        st.warning(item)
    st.download_button("Download hypothesis report", to_markdown(result),
                       "scientific_hypothesis_report.md", mime="text/markdown")

with st.expander("Generation history"):
    for row in reversed(load_generations("data/hypotheses.jsonl", 10)):
        st.write(f"{row['field']} · {row['observation'][:90]} · {row['created_at'][:10]}")
