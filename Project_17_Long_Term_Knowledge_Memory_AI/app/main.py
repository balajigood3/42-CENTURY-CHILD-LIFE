import streamlit as st
from app.core import OllamaClient,extract_memories,answer_with_memory
from app.storage import MemoryStore

st.set_page_config(page_title="Long-Term Knowledge Memory AI",layout="wide")
st.title("Long-Term Knowledge Memory AI")
st.caption("A local, user-controlled memory store with extraction, retrieval, and deletion controls.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    host=st.text_input("Ollama host","http://localhost:11434")
    st.warning("Review every extracted memory before relying on it. Avoid entering secrets or sensitive data.")
store=MemoryStore()
st.metric("Active memories",store.count())
tab1,tab2,tab3=st.tabs(["Add memories","Ask with memory","Manage memories"])
with tab1:
    text=st.text_area("Enter notes or preferences to remember",height=180,
        placeholder="Example: I prefer Python examples and free/open-source tools.")
    source=st.text_input("Source label","user_note")
    if st.button("Extract and save memories",type="primary",disabled=not text.strip()):
        try:
            with st.spinner("Extracting durable facts..."):
                items=extract_memories(text,OllamaClient(model,host),source)
            st.subheader("Review extracted memories")
            if items:
                approved=[]
                for i,item in enumerate(items):
                    if st.checkbox(f"{item['memory']}  ·  {item['category']} · importance {item['importance']}",value=True,key=f"mem_{i}"):
                        approved.append(item)
                if st.button("Save selected memories"):
                    st.success(f"Saved or updated {store.add_many(approved)} memory records.")
            else: st.info("No durable memories were extracted.")
        except Exception as e: st.error(str(e))
with tab2:
    query=st.text_input("Ask a question")
    if st.button("Answer using memory",disabled=not query.strip()):
        try:
            with st.spinner("Retrieving relevant memories..."):
                answer,selected=answer_with_memory(query,store.all(),OllamaClient(model,host))
            st.subheader("Answer"); st.write(answer)
            with st.expander("Memories used"):
                if selected: st.json(selected)
                else: st.write("No relevant memories found.")
        except Exception as e: st.error(str(e))
with tab3:
    rows=store.all()
    if not rows: st.info("No active memories.")
    for m in rows:
        col1,col2=st.columns([5,1])
        col1.write(f"**#{m['id']}** {m['memory']}  \n{m['category']} · importance {m['importance']} · source {m['source']}")
        if col2.button("Deactivate",key=f"del_{m['id']}"):
            store.deactivate(m["id"]); st.rerun()
    st.divider()
    if st.button("Permanently delete all memories"):
        st.session_state["confirm_clear"]=True
    if st.session_state.get("confirm_clear"):
        st.warning("This permanently deletes the local memory database records.")
        if st.button("Confirm permanent deletion"):
            store.clear_all(); st.session_state["confirm_clear"]=False; st.rerun()
