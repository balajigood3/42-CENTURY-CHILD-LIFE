import json
import streamlit as st
from app.research import conduct_research, ResearchError

st.set_page_config(page_title="Autonomous Research Agent", layout="wide")
st.title("Autonomous Research Agent")
st.caption("Discover or accept sources → extract evidence → synthesize a cited research brief.")
topic = st.text_input("Research topic", "Open-source large language model deployment")
urls_text = st.text_area("Optional source URLs (one per line)", placeholder="https://example.com/article")
max_sources = st.slider("Maximum sources", 1, 8, 5)
if st.button("Start research", type="primary"):
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()] or None
    with st.spinner("Collecting and analyzing sources..."):
        try:
            result = conduct_research(topic, urls=urls, max_sources=max_sources)
            st.subheader("Research report")
            st.markdown(result["report"])
            st.subheader("Sources")
            for i, source in enumerate(result["sources"], 1):
                st.markdown(f"{i}. [{source['title']}]({source['url']})")
            st.download_button("Download source manifest", json.dumps(result["sources"], indent=2),
                               file_name="research_sources.json", mime="application/json")
        except ResearchError as exc:
            st.error(str(exc))
st.info("Requires network access for source retrieval and a local Ollama model for synthesis.")
