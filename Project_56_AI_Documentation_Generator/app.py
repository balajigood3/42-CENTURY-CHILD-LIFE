import streamlit as st
from docgen.engine import generate_documentation,make_zip
st.set_page_config(page_title="AI Documentation Generator",layout="wide")
st.title("AI Documentation Generator")
st.caption("AST-based Python documentation generator. No paid API keys.")
up=st.file_uploader("Upload Python file",type=["py"])
src=st.text_area("Or paste Python source",height=300,placeholder="def add(a: int, b: int):\n    return a+b")
name=st.text_input("Project / module name","sample_project")
if st.button("Generate documentation",type="primary"):
 try:
  code=up.getvalue().decode("utf-8") if up else src
  r=generate_documentation(code,name);st.session_state["result"]=r;st.session_state["zip"]=make_zip(r)
 except (ValueError,UnicodeDecodeError) as e: st.error(str(e))
if "result" in st.session_state:
 r=st.session_state["result"]
 st.success(f"Generated docs for {r['summary']['functions']} function(s), {r['summary']['classes']} class(es).")
 t1,t2,t3,t4=st.tabs(["README","API Reference","Architecture","Analysis"])
 with t1: st.markdown(r["README.md"])
 with t2: st.markdown(r["API_REFERENCE.md"])
 with t3: st.markdown(r["ARCHITECTURE.md"])
 with t4: st.json(r["analysis"])
 st.download_button("Download documentation ZIP",st.session_state["zip"],"generated_documentation.zip","application/zip")
