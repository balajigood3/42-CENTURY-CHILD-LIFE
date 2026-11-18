import hashlib
import streamlit as st
from app.core import split_document, rank_chunks, generate_answer, OllamaClient, summarize_learning
from app.storage import KnowledgeStore

st.set_page_config(page_title="Continuous Learning Knowledge AI", layout="wide")
st.title("Continuous Learning Knowledge AI")
st.caption("Incrementally updates a knowledge base, tracks document versions, and uses feedback to improve retrieval ranking.")

with st.sidebar:
    model = st.text_input("Ollama model", "qwen2.5:3b")
    host = st.text_input("Ollama host", "http://localhost:11434")
    chunk_size = st.slider("Chunk size", 400, 1600, 900, 50)
    overlap = st.slider("Chunk overlap", 0, 250, 120, 10)
    top_k = st.slider("Retrieved chunks", 1, 10, 5)
    st.info("Local Ollama inference. No paid API key.")

store = KnowledgeStore()
uploads = st.file_uploader("Add or update TXT / Markdown documents", type=["txt","md"], accept_multiple_files=True)
if st.button("Ingest knowledge", type="primary", disabled=not uploads):
    for f in uploads:
        text = f.getvalue().decode("utf-8", errors="replace")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        chunks = split_document(text, f.name, 1, chunk_size, overlap)
        version, count, changed = store.ingest(f.name, digest, chunks)
        if changed:
            st.success(f"{f.name}: stored version {version} ({count} chunks).")
        else:
            st.info(f"{f.name}: unchanged; existing version {version} retained.")

chunks = store.active_chunks()
stats = store.stats()
st.subheader("Knowledge base status")
st.write(summarize_learning(stats))
if chunks:
    query = st.text_area("Ask a question about the knowledge base")
    if st.button("Retrieve and answer", type="primary", disabled=not query.strip()):
        try:
            ranked = rank_chunks(query, chunks, store.feedback_summary(), top_k)
            with st.spinner("Generating evidence-grounded answer..."):
                answer = generate_answer(query, ranked, OllamaClient(model, host))
            st.session_state["last_answer"] = answer
            st.session_state["last_results"] = ranked
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Retrieved evidence and feedback")
            for item in ranked:
                with st.expander(f"{item['source']} · v{item['version']} · score {item['score']:.3f}"):
                    st.write(item["text"])
                    st.caption(f"Lexical score {item['lexical_score']:.3f}; feedback boost {item['feedback_boost']:.3f}")
                    rating = st.radio("Rate relevance", [1,2,3,4,5], horizontal=True,
                                      key=f"rating_{item['id']}")
                    comment = st.text_input("Optional feedback", key=f"comment_{item['id']}")
                    if st.button("Submit feedback", key=f"submit_{item['id']}"):
                        store.add_feedback(item["id"], rating, comment)
                        st.success("Feedback saved and will influence future ranking.")
        except Exception as exc:
            st.error(str(exc))
else:
    st.info("Upload documents to start building the knowledge base.")

with st.expander("Document version history"):
    rows = store.document_versions()
    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.write("No documents ingested yet.")
