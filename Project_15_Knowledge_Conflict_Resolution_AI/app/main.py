import streamlit as st,json
from app.core import OllamaClient,analyze_documents,report_markdown
from app.storage import Store
st.set_page_config(page_title="Knowledge Conflict Resolver",layout="wide")
st.title("Knowledge Conflict Resolution AI")
st.caption("Compare source-linked claims; identify conflicts without automatically declaring truth.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    host=st.text_input("Ollama host","http://localhost:11434")
    threshold=st.slider("Candidate lexical similarity",.05,.6,.12,.01)
    st.info("Requires local Ollama. No paid API key.")
uploads=st.file_uploader("Upload at least two TXT/MD files",type=["txt","md"],accept_multiple_files=True)
if st.button("Analyze conflicts",type="primary",disabled=not uploads or len(uploads)<2):
    docs={f.name:f.getvalue().decode("utf-8",errors="replace") for f in uploads}
    try:
        with st.spinner("Extracting claims and comparing pairs..."):
            claims,conflicts=analyze_documents(docs,OllamaClient(model,host),threshold)
            report=report_markdown(claims,conflicts); Store().save(list(docs),claims,report)
        st.success(f"Completed: {len(claims)} claims; {len(conflicts)} comparisons.")
        st.download_button("Download report",report,"conflict_report.md","text/markdown")
        for i,c in enumerate(conflicts,1):
            with st.expander(f"{i}. {c.classification} — {c.severity}"):
                st.write(f"**{c.source_a}:** {c.claim_a}")
                st.write(f"**{c.source_b}:** {c.claim_b}")
                st.write("Explanation:",c.explanation)
                st.write("Resolution path:",c.resolution)
                st.write("Evidence needed:",c.evidence_needed)
                st.metric("Uncalibrated model confidence",f"{c.confidence:.0%}")
        with st.expander("Extracted claims"): st.json(claims)
    except Exception as e: st.error(str(e))
st.divider(); st.subheader("Recent local analyses")
try:
    for row in Store().recent(): st.write(f"#{row[0]} · {row[1]} · {', '.join(json.loads(row[2]))}")
except Exception as e: st.caption(str(e))
