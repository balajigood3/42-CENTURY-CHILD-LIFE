import streamlit as st
from app.core import split_chunks, retrieve, answer_query, OllamaClient
from app.storage import ChunkStore

st.set_page_config(page_title="Context-Aware Retrieval AI", layout="wide")
st.title("Context-Aware Retrieval AI")
st.caption("Retrieves evidence using the latest question, conversation context, and document metadata.")

with st.sidebar:
    model = st.text_input("Ollama model", "qwen2.5:3b")
    host = st.text_input("Ollama host", "http://localhost:11434")
    chunk_size = st.slider("Chunk size", 400, 1600, 850, 50)
    overlap = st.slider("Chunk overlap", 0, 250, 120, 10)
    top_k = st.slider("Top retrieved chunks", 1, 10, 5)
    language = st.selectbox("Answer language", ["auto", "Tamil", "English", "Hindi", "Telugu", "Kannada", "Malayalam"])
    st.info("Local Ollama inference. No paid API key.")

store = ChunkStore()
if "history" not in st.session_state:
    st.session_state.history = []
uploads = st.file_uploader("Upload TXT / Markdown documents", type=["txt","md"], accept_multiple_files=True)
category = st.text_input("Category for uploaded documents", "general")
if st.button("Index / update documents", type="primary", disabled=not uploads):
    count = 0
    for f in uploads:
        text = f.getvalue().decode("utf-8", errors="replace")
        chunks = split_chunks(text, f.name, category.strip() or "general", chunk_size, overlap)
        store.replace_source(f.name, chunks)
        count += len(chunks)
    st.success(f"Indexed or updated {len(uploads)} documents into {count} chunks.")

chunks = store.all_chunks()
if chunks:
    st.write(f"**Knowledge base:** {len(chunks)} chunks · {len(store.sources())} documents")
    categories = ["All"] + store.categories()
    sources = ["All"] + store.sources()
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Filter category", categories)
    with col2:
        selected_source = st.selectbox("Filter source", sources)
    query = st.text_area("Question / follow-up question", placeholder="Example: What are its main benefits?", height=90)
    if st.button("Retrieve and answer", type="primary", disabled=not query.strip()):
        try:
            client = OllamaClient(model, host)
            results = retrieve(query, chunks, st.session_state.history,
                               selected_category, selected_source, top_k, client)
            with st.spinner("Generating context-aware answer..."):
                answer = answer_query(query, results, st.session_state.history, client, language)
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Retrieved evidence")
            if results:
                for r in results:
                    with st.expander(f"{r['source']} · {r['category']} · score {r['score']:.3f}"):
                        st.write(r["text"])
            else:
                st.warning("No matching evidence found. Try changing the filters or query.")
            st.session_state.history.extend([
                {"role":"user","content":query},
                {"role":"assistant","content":answer}
            ])
        except Exception as exc:
            st.error(str(exc))
    with st.expander("Conversation context"):
        for turn in st.session_state.history[-10:]:
            st.markdown(f"**{turn['role'].title()}:** {turn['content']}")
        if st.button("Clear conversation context"):
            st.session_state.history = []
            st.rerun()
else:
    st.info("Upload documents to create the searchable knowledge base. Example documents are in examples/.")
