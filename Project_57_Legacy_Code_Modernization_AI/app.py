import os, tempfile
import streamlit as st
from legacy_modernizer.analyzer import analyze_source, conservative_modernize, ModernizationError
from legacy_modernizer.exporter import export_bundle

st.set_page_config(page_title="Legacy Code Modernization AI", layout="wide")
st.title("Legacy Code Modernization AI")
st.caption("AST-based modernization advisor • local processing • no paid API keys")
sample = """import os
from typing import List

def read_names(path):
    try:
        return open(path).read().splitlines()
    except:
        return []

def greet(name):
    return "Hello, {}".format(name)
"""
source = st.text_area("Paste Python source", value=sample, height=320)
filename = st.text_input("Source filename", "legacy.py")
if st.button("Analyze and prepare report", type="primary"):
    try:
        report = analyze_source(source)
        modernized = conservative_modernize(source)
        st.subheader("Analysis summary")
        st.json(report["summary"])
        st.subheader("Findings")
        if report["findings"]:
            st.dataframe(report["findings"], use_container_width=True)
        else:
            st.success("No configured patterns detected.")
        left, right = st.columns(2)
        with left:
            st.markdown("**Original source**")
            st.code(source, language="python")
        with right:
            st.markdown("**Conservative output**")
            st.code(modernized, language="python")
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        export_bundle(source, tmp_path, filename)
        with open(tmp_path, "rb") as handle:
            st.download_button("Download report bundle", handle.read(), file_name="modernization_bundle.zip")
        os.unlink(tmp_path)
    except ModernizationError as exc:
        st.error(str(exc))
st.info("This tool reports opportunities; it does not automatically rewrite program logic. Review recommendations and run tests before applying changes.")
