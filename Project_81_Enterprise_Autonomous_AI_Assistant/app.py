import streamlit as st
from enterprise_assistant.assistant import (
    load_documents, retrieve_documents, create_action_request
)
from enterprise_assistant.llm import ask_ollama
from enterprise_assistant.storage import save_record, load_records

st.set_page_config(page_title="Enterprise Autonomous AI Assistant", layout="wide")
st.title("Enterprise Autonomous AI Assistant")
st.caption("நிறுவன அறிவுத் தகவல்களைத் தேடி பதிலளிக்கும் மற்றும் approval தேவைப்படும் செயல்களை draft செய்யும் local-first assistant.")

try:
    docs = load_documents()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.subheader("Access context")
    role = st.selectbox("User role", ["Employee", "Manager", "IT Admin"])
    departments = ["All"] + sorted({d["department"] for d in docs})
    department = st.selectbox("Knowledge department", departments)
    model = st.text_input("Ollama model", "qwen2.5:3b")
    mode = st.radio("Answer mode", ["Local Ollama AI", "Offline retrieval"])

st.markdown("### Ask enterprise knowledge")
question = st.text_area("Your question", placeholder="e.g. What is the expense submission process?")
if st.button("Ask assistant", type="primary", disabled=not question.strip()):
    retrieved = retrieve_documents(question, docs, department)
    try:
        if mode == "Local Ollama AI":
            response = ask_ollama(question, retrieved, role, model=model)
        else:
            response = {
                "answer": ("Relevant internal excerpts:\n\n" + "\n\n".join(
                    f"**{d['title']} ({d['id']})**\n{d['content']}" for d in retrieved
                )) if retrieved else "No matching internal documents were found. Please refine your question.",
                "citations": [d["id"] for d in retrieved],
                "follow_up_questions": ["Which department or policy area do you mean?"],
                "action_suggestion": "No action has been performed."
            }
        st.session_state["enterprise_response"] = response
        st.session_state["retrieved_docs"] = retrieved
        save_record("data/audit.jsonl", {"event": "knowledge_query", "role": role,
                    "question": question, "citations": response["citations"]})
    except (RuntimeError, ValueError) as exc:
        st.error(str(exc))

if st.session_state.get("enterprise_response"):
    response = st.session_state["enterprise_response"]
    st.markdown("### Answer")
    st.write(response["answer"])
    st.caption("Sources: " + (", ".join(response["citations"]) or "No source cited"))
    for q in response["follow_up_questions"]:
        st.markdown(f"- Follow-up: {q}")
    if response["action_suggestion"]:
        st.info("Suggested action only: " + response["action_suggestion"])

st.divider()
st.markdown("### Draft an approval-gated request")
with st.form("action_form"):
    requester = st.text_input("Requester identifier (work alias)")
    action_type = st.selectbox("Request type", ["Leave request", "Expense review", "IT support ticket"])
    details = st.text_area("Request details")
    action_submitted = st.form_submit_button("Create draft request")
if action_submitted:
    try:
        request = create_action_request(action_type, details, requester, role)
        save_record("data/action_requests.jsonl", {"event": "action_request", **request})
        st.session_state["last_action"] = request
    except ValueError as exc:
        st.error(str(exc))
if st.session_state.get("last_action"):
    st.warning(st.session_state["last_action"]["notice"])
    st.json(st.session_state["last_action"])

with st.expander("Recent audit events"):
    for record in reversed(load_records("data/audit.jsonl", 10)):
        st.write(f"{record.get('event')} · {record.get('role')} · {record.get('created_at', '')[:19]}")
