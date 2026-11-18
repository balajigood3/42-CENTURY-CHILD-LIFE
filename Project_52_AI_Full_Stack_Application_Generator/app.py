import streamlit as st
from generator.spec import parse_spec
from generator.builder import build_project,make_zip
st.set_page_config(page_title="AI Full-Stack Generator",layout="wide")
st.title("AI Full-Stack Application Generator")
st.caption("React + FastAPI + SQLite scaffold generator. No paid API keys.")
name=st.text_input("Application name","Inventory Manager")
entity=st.text_input("Entity name","Product")
fields=st.text_input("Fields (name:type, comma separated)","name:str, quantity:int, price:float")
if st.button("Generate scaffold",type="primary"):
 try:
  f=build_project(parse_spec(name,entity,fields)); st.session_state["files"]=f; st.session_state["zip"]=make_zip(f); st.success(f"Generated {len(f)} files.")
 except ValueError as e: st.error(str(e))
if "files" in st.session_state:
 names=sorted(st.session_state["files"]); selected=st.selectbox("Preview file",names); st.code(st.session_state["files"][selected])
 st.download_button("Download generated app ZIP",st.session_state["zip"],file_name="generated_full_stack_app.zip",mime="application/zip")
