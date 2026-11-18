import json
import streamlit as st
from adversarial_tester.engine import DEFAULT_TESTS, run_suite, load_tests

st.set_page_config(page_title="Adversarial Prompt Testing AI", page_icon="🧪", layout="wide")
st.title("Adversarial Prompt Testing AI")
st.caption("Local prompt-risk test harness. It classifies test strings; it does not execute prompts or call an LLM.")
test_text = st.text_area("Test suite (JSON array)", json.dumps(DEFAULT_TESTS, indent=2), height=360)
response_text = st.text_area("Optional model responses (JSON object keyed by test ID)", "{}", height=130)
if st.button("Run test suite", type="primary"):
    try:
        cases = load_tests(json.loads(test_text))
        responses = json.loads(response_text)
        if not isinstance(responses, dict):
            raise ValueError("Responses must be a JSON object keyed by test ID.")
        report = run_suite(cases, responses)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total tests", report["total_tests"])
        c2.metric("Prompt risk cases", report["prompt_risk_cases"])
        c3.metric("Flagged responses", report["response_flagged_cases"])
        st.dataframe(report["results"], use_container_width=True)
        st.download_button("Download JSON report", json.dumps(report, indent=2), "adversarial-test-report.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
