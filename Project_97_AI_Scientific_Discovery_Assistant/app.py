import json
import streamlit as st
import pandas as pd
from scientific_discovery.engine import analyze_research, build_hypothesis_templates

st.set_page_config(page_title="AI Scientific Discovery Assistant", layout="wide")
st.title("AI Scientific Discovery Assistant")
st.caption("Research notes-ஐ ஆய்வு செய்து keywords, question coverage, candidate research gaps மற்றும் hypothesis templates உருவாக்கும் local assistant.")

st.info("This is a literature-triage prototype using keyword overlap. It does not search the web, verify papers, or establish scientific discoveries.")
question = st.text_area("Research question", "How does data augmentation affect model robustness?")
uploaded = st.file_uploader("Upload research notes (.txt or .md)", type=["txt", "md"], accept_multiple_files=True)
manual_title = st.text_input("Additional note title", "Study Notes")
manual_text = st.text_area("Additional research text", "Data augmentation improves robustness on image classification benchmarks. Evaluation uses accuracy and corruption error.")
top_k = st.slider("Top terms", 1, 30, 10)
if st.button("Analyze research", type="primary"):
    docs = []
    for f in uploaded or []:
        docs.append({"title": f.name, "text": f.getvalue().decode("utf-8", errors="replace")})
    if manual_text.strip():
        docs.append({"title": manual_title, "text": manual_text})
    try:
        result = analyze_research(docs, question, top_k)
        result["hypothesis_templates"] = build_hypothesis_templates(question, result["question_terms_not_found"])
        st.session_state.discovery_result = result
    except ValueError as exc:
        st.error(str(exc))

if "discovery_result" in st.session_state:
    result = st.session_state.discovery_result
    st.metric("Documents analyzed", result["document_count"])
    st.subheader("Document relevance")
    st.dataframe(pd.DataFrame(result["documents"]), use_container_width=True)
    st.subheader("Frequent terms")
    st.dataframe(pd.DataFrame(result["frequent_terms"]), use_container_width=True)
    st.subheader("Question terms not found")
    st.write(", ".join(result["question_terms_not_found"]) or "All question keywords appear in supplied notes.")
    st.subheader("Candidate research gaps")
    for item in result["candidate_research_gaps"]:
        st.write("• " + item)
    st.subheader("Candidate hypothesis")
    st.json(result["hypothesis_templates"])
    st.download_button("Download research analysis JSON",
                       json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="scientific_discovery_report.json", mime="application/json")
