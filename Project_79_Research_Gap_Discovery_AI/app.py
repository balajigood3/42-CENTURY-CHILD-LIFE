import streamlit as st
from research_gap.analyzer import offline_analysis, to_markdown
from research_gap.llm import analyze_research
from research_gap.storage import save_analysis, load_analyses

st.set_page_config(page_title="Research Gap Discovery AI", layout="wide")
st.title("Research Gap Discovery AI")
st.caption("உங்கள் literature notes-ஐ ஆராய்ந்து சாத்தியமான research gaps மற்றும் அடுத்த ஆய்வு திசைகளை உருவாக்குங்கள்.")

with st.form("research_form"):
    field = st.text_input("Research field", placeholder="e.g. Explainable AI in healthcare")
    question = st.text_area("Research question / problem statement")
    notes = st.text_area("Literature notes",
                         placeholder="Paste summaries or notes from papers. Add [P1], [P2] identifiers for traceability.",
                         height=240)
    constraints = st.text_area("Context / constraints (optional)",
                               placeholder="Population, geography, timeframe, methods of interest...")
    model = st.text_input("Ollama model", "qwen2.5:3b")
    mode = st.radio("Analysis mode", ["Local Ollama AI", "Offline note review"], horizontal=True)
    submitted = st.form_submit_button("Discover candidate gaps", type="primary")

if submitted:
    try:
        result = (analyze_research(field, question, notes, constraints, model=model)
                  if mode == "Local Ollama AI" else offline_analysis(field, question, notes))
        st.session_state["gap_analysis"] = result
        save_analysis("data/research_analyses.jsonl", field, question, result)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

if st.session_state.get("gap_analysis"):
    result = st.session_state["gap_analysis"]
    st.subheader(result["field"])
    st.markdown("### Literature synthesis")
    st.write(result["literature_synthesis"])
    st.markdown("### Candidate research gaps")
    for i, gap in enumerate(result["candidate_gaps"], 1):
        with st.expander(f"{i}. {gap['gap']} · {gap['confidence']} confidence", expanded=True):
            st.write(f"**Type:** {gap['gap_type']}")
            st.write(gap["rationale"])
            st.markdown("**Evidence from supplied notes**")
            if gap["evidence_from_notes"]:
                for evidence in gap["evidence_from_notes"]:
                    st.markdown(f"- {evidence}")
            else:
                st.caption("No note excerpts attached.")
    st.markdown("### Possible research directions")
    for i, direction in enumerate(result["research_directions"], 1):
        st.markdown(f"**{i}. {direction['title']}**")
        st.write(f"Objective: {direction['objective']}")
        st.write(f"Method: {direction['method']}")
        st.write(f"Validation: {direction['validation']}")
    st.markdown("### Limitations")
    for item in result["limitations"]:
        st.warning(item)
    st.markdown("### Next steps")
    for item in result["next_steps"]:
        st.markdown(f"- {item}")
    st.download_button("Download research gap report", to_markdown(result),
                       "research_gap_analysis.md", mime="text/markdown")

with st.expander("Previous analyses"):
    for record in reversed(load_analyses("data/research_analyses.jsonl", 10)):
        st.write(f"{record['field']} · {record['question'][:90]} · {record['created_at'][:10]}")
