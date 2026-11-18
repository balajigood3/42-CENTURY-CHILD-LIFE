import json
import streamlit as st
from app.builder import build_project, BuilderError

st.set_page_config(page_title="AI Project Builder Agent", layout="wide")
st.title("AI Project Builder Agent")
st.caption("Generate a bounded Python starter project from a plain-language specification.")
name = st.text_input("Project name", "Personal Expense Tracker")
description = st.text_area(
    "Project description",
    "A command-line Python application that records expenses in a local JSON file and displays total spending.",
    height=130
)
use_llm = st.toggle("Use local Ollama to generate files", value=True)
if st.button("Build project", type="primary"):
    try:
        result = build_project(name, description, use_llm=use_llm)
        st.success(f"Project created at: {result['path']}")
        st.json(result["manifest"])
        st.info("Files are created in generated_projects/. Review generated code before running it.")
    except BuilderError as exc:
        st.error(str(exc))
st.warning("Generated code is untrusted. Inspect it before execution. This app does not run generated code.")
