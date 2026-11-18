import json
import tempfile
from pathlib import Path
import streamlit as st
from contract_analyzer.analyzer import analyze_contract, extract_text_from_pdf
from contract_analyzer.exporter import export_markdown

st.set_page_config(page_title="Intelligent Contract Analyzer", layout="wide")
st.title("Intelligent Contract Analyzer")
st.caption("ஒப்பந்தத்தின் முக்கிய clauses, metadata, risk flags மற்றும் review checklist-ஐ கண்டறியும் local-first tool.")
st.warning("Demo issue-spotting only — இது சட்ட ஆலோசனை அல்ல. முக்கிய ஒப்பந்த முடிவுகளுக்கு qualified lawyer-ஐ அணுகவும்.")

uploaded = st.file_uploader("Upload TXT or PDF contract", type=["txt", "pdf"])
pasted = st.text_area("Or paste contract text", height=220, placeholder="Paste agreement text here...")
if st.button("Analyze contract", type="primary"):
    try:
        if uploaded:
            if uploaded.size > 10 * 1024 * 1024:
                raise ValueError("Upload must be 10 MB or smaller.")
            suffix = Path(uploaded.name).suffix.lower()
            if suffix == ".pdf":
                with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                    tmp.write(uploaded.getvalue())
                    tmp.flush()
                    contract_text = extract_text_from_pdf(tmp.name)
            else:
                contract_text = uploaded.getvalue().decode("utf-8-sig")
            filename = uploaded.name
        else:
            contract_text, filename = pasted, "pasted_contract.txt"
        result = analyze_contract(contract_text, filename)
        st.session_state["analysis_result"] = result
    except (ValueError, RuntimeError, UnicodeDecodeError) as exc:
        st.error(str(exc))

result = st.session_state.get("analysis_result")
if result:
    st.success("Contract review completed.")
    meta = result["metadata"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Detected clause types", len(result["clauses"]))
    c2.metric("Risk flags", len(result["risk_flags"]))
    c3.metric("Clauses not detected", len(result["clauses_not_detected"]))
    st.subheader("Possible metadata")
    st.write("Parties:", meta["possible_parties"] or "Not detected")
    st.write("Date strings:", meta["date_strings"] or "Not detected")
    st.subheader("Detected clauses")
    for clause in result["clauses"]:
        with st.expander(clause["clause_type"].replace("_", " ").title()):
            for excerpt in clause["excerpts"]:
                st.write(excerpt)
    st.subheader("Risk flags")
    if result["risk_flags"]:
        st.dataframe(result["risk_flags"], use_container_width=True)
    else:
        st.info("No configured risk patterns were detected. This does not mean the contract is risk-free.")
    st.subheader("Clauses not detected")
    st.write(result["clauses_not_detected"])
    st.subheader("Review checklist")
    for item in result["review_checklist"]:
        st.checkbox(item, key="check_" + str(abs(hash(item))))
    st.download_button("Download JSON report", json.dumps(result, ensure_ascii=False, indent=2),
                       file_name="contract_review.json", mime="application/json")
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "contract_review.md"
        export_markdown(result, md)
        report = md.read_text(encoding="utf-8")
    st.download_button("Download Markdown report", report,
                       file_name="contract_review.md", mime="text/markdown")
    st.caption(result["disclaimer"])
