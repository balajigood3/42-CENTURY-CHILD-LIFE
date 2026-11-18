import json
import streamlit as st
from .store import init_db, list_documents, delete_document
from .ingest import ingest_file
from .qa import answer_question
from .security import normalize_role

st.set_page_config(page_title="Secure RAG Assistant", page_icon="🔒", layout="wide")
st.title("Secure RAG Assistant")
st.caption("Role-filtered document retrieval with source references and basic prompt-injection safeguards")
st.warning("Demo authentication: the role selector is not real identity verification. Production must derive roles from a trusted identity provider.")

init_db()
role = normalize_role(st.selectbox("Demo user role", ["user", "staff", "admin"]))

with st.expander("1. Add knowledge documents", expanded=True):
    uploads = st.file_uploader("Upload TXT, MD, CSV, or text-based PDF", type=["txt","md","csv","pdf"], accept_multiple_files=True)
    allowed = st.multiselect("Who can access these documents?", ["admin","staff","user"], default=["admin","staff"])
    if st.button("Ingest selected documents", disabled=not uploads or not allowed):
        for upload in uploads:
            try:
                count = ingest_file(upload.name, upload.getvalue(), allowed)
                st.success(f"{upload.name}: {count} chunk(s) indexed.")
            except Exception as exc:
                st.error(f"{upload.name}: {exc}")

st.subheader("2. Authorized knowledge base")
docs = list_documents()
if docs:
    st.dataframe(docs, use_container_width=True, hide_index=True)
    if role == "admin":
        names = [d["doc_name"] for d in docs]
        selected_delete = st.selectbox("Admin: select a document to delete", [""] + names)
        if st.button("Delete selected document", disabled=not selected_delete):
            delete_document(selected_delete)
            st.rerun()
else:
    st.info("No documents indexed yet.")

st.subheader("3. Ask a question")
question = st.text_input("Question", placeholder="What is the employee leave policy?")
if st.button("Search authorized documents", type="primary", disabled=not question.strip()):
    result = answer_question(question, role)
    st.session_state["qa_result"] = result

if "qa_result" in st.session_state:
    result = st.session_state["qa_result"]
    st.markdown("**Answer**")
    st.write(result["answer"])
    if result["warnings"]:
        for warning in result["warnings"]:
            st.warning(warning)
    if result["citations"]:
        st.markdown("**Source citations**")
        st.dataframe(result["citations"], use_container_width=True, hide_index=True)
    st.download_button("Download answer report", json.dumps(result, indent=2), "secure_rag_answer.json", "application/json")

st.caption("Retrieval is extractive and local. Access control is applied before ranking; this demo does not use a generative LLM.")
