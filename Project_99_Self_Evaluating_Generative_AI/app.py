import json
import pandas as pd
import streamlit as st
from evaluator.engine import evaluate_batch, summarize_failures

st.set_page_config(page_title="Self-Evaluating Generative AI", layout="wide")
st.title("Self-Evaluating Generative AI")
st.caption("Generated answers-ஐ measurable criteria மூலம் evaluate செய்யும் local evaluation workbench.")

example = [
    {
        "id": "case-1",
        "answer": "RAG combines retrieval with generation. It retrieves relevant documents and uses them as context for an answer.",
        "expected_keywords": ["retrieval", "generation", "documents"],
        "required_phrases": ["relevant documents"],
        "forbidden_phrases": ["guaranteed correct"],
        "min_words": 10,
        "max_words": 80
    },
    {
        "id": "case-2",
        "answer": "A vector database stores embeddings for similarity search.",
        "expected_keywords": ["embedding", "similarity"],
        "required_phrases": ["vector database"],
        "forbidden_phrases": ["always perfect"],
        "min_words": 5,
        "max_words": 50
    }
]
raw = st.text_area("Evaluation test cases (JSON)", json.dumps(example, indent=2), height=360)
if st.button("Evaluate answers", type="primary"):
    try:
        cases = json.loads(raw)
        if not isinstance(cases, list):
            raise ValueError("Top-level JSON must be a list of test cases.")
        report = evaluate_batch(cases)
        st.session_state.eval_report = report
    except Exception as exc:
        st.error(f"Evaluation failed: {exc}")

if "eval_report" in st.session_state:
    report = st.session_state.eval_report
    c1, c2, c3 = st.columns(3)
    c1.metric("Pass rate", f"{report['pass_rate']:.0%}")
    c2.metric("Average score", f"{report['average_score']}/100")
    c3.metric("Failed cases", report["failed_cases"])
    st.subheader("Per-case results")
    frame = pd.DataFrame([
        {"Case": x["case_id"], "Passed": x["passed"], "Score": x["score"],
         "Words": x["word_count"], "Missing required": ", ".join(x["missing_required_phrases"]),
         "Forbidden hits": ", ".join(x["forbidden_phrase_hits"])}
        for x in report["results"]
    ])
    st.dataframe(frame, use_container_width=True)
    st.subheader("Failure analysis")
    st.json(summarize_failures(report))
    st.download_button("Download evaluation report",
                       json.dumps(report, indent=2), "evaluation_report.json",
                       mime="application/json")
