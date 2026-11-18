import json
import streamlit as st
from support_agent.knowledge import load_faqs
from support_agent.agent import draft_response, create_ticket
from support_agent.storage import append_record, recent_records

st.set_page_config(page_title="AI Customer Support Agent", layout="wide")
st.title("AI Customer Support Agent")
st.caption("Customer கேள்விகளுக்கு FAQ ஆதாரத்துடன் பதில் draft செய்து, தேவையானபோது human support ticket உருவாக்கும் local-first assistant.")
try:
    faqs = load_faqs()
except ValueError as exc:
    st.error(str(exc))
    st.stop()

tab1, tab2, tab3 = st.tabs(["Ask support", "Create ticket", "FAQ knowledge"])
with tab1:
    message = st.text_area("Customer message", placeholder="Where is my order?")
    if st.button("Generate support response", type="primary"):
        try:
            result = draft_response(message, faqs)
            st.session_state["support_result"] = result
            append_record("data/audit.jsonl", {
                "event": "support_query", "intent": result["intent"],
                "citations": result["citations"], "message": result["safe_message"]
            })
        except ValueError as exc:
            st.error(str(exc))
    result = st.session_state.get("support_result")
    if result:
        st.markdown("### Suggested response")
        st.write(result["answer"])
        st.caption(f"Intent: {result['intent']} · Evidence: {result['confidence']}")
        st.write("FAQ sources:", result["citations"] or "No FAQ source")
        if result["handoff_recommended"]:
            st.warning("Human support handoff recommended.")
        st.caption(result["disclaimer"])

with tab2:
    with st.form("ticket"):
        customer_ref = st.text_input("Customer reference (not password)")
        ticket_message = st.text_area("Issue details")
        priority = st.selectbox("Priority", ["Low", "Normal", "High"])
        submitted = st.form_submit_button("Create ticket draft")
    if submitted:
        try:
            ticket = create_ticket(customer_ref, ticket_message, priority)
            append_record("data/tickets.jsonl", ticket)
            st.session_state["last_ticket"] = ticket
        except ValueError as exc:
            st.error(str(exc))
    if st.session_state.get("last_ticket"):
        st.info(st.session_state["last_ticket"]["notice"])
        st.json(st.session_state["last_ticket"])

with tab3:
    st.write(f"{len(faqs)} FAQ entries loaded from data/faqs.json.")
    st.dataframe(faqs, use_container_width=True)

with st.expander("Recent audit events"):
    for record in reversed(recent_records("data/audit.jsonl", 10)):
        st.write(f"{record.get('event')} · {record.get('intent')} · {record.get('created_at', '')[:19]}")
