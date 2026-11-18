import streamlit as st
from app.core import chunk_text, MultilingualRetriever, OllamaClient, generate_answer, format_sources

st.set_page_config(page_title="Multilingual RAG Assistant", layout="wide")
st.title("Multilingual RAG Assistant")
st.caption("Ask questions in Tamil, English, Hindi, Telugu, Kannada, Malayalam and other languages using your own documents.")

with st.sidebar:
    model = st.text_input("Ollama model", "qwen2.5:3b")
    host = st.text_input("Ollama host", "http://localhost:11434")
    chunk_size = st.slider("Chunk size (characters)", 400, 1800, 900, 100)
    overlap = st.slider("Chunk overlap", 0, 300, 120, 20)
    top_k = st.slider("Retrieved chunks", 1, 10, 5)
    answer_language = st.selectbox("Answer language", ["auto", "Tamil", "English", "Hindi", "Telugu", "Kannada", "Malayalam"])
    st.info("Local Ollama inference. No paid API key.")

if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "retriever" not in st.session_state:
    st.session_state.retriever = MultilingualRetriever()

uploads = st.file_uploader("Upload UTF-8 TXT / Markdown documents", type=["txt", "md"], accept_multiple_files=True)
if st.button("Index documents", type="primary", disabled=not uploads):
    all_chunks = []
    for f in uploads:
        body = f.getvalue().decode("utf-8", errors="replace")
        all_chunks.extend(chunk_text(body, f.name, chunk_size, overlap))
    st.session_state.chunks = all_chunks
    st.session_state.retriever.fit(all_chunks)
    st.success(f"Indexed {len(uploads)} documents into {len(all_chunks)} chunks.")

if st.session_state.chunks:
    st.metric("Indexed chunks", len(st.session_state.chunks))
    query = st.text_area("Your question / உங்கள் கேள்வி", height=100)
    if st.button("Retrieve and answer", disabled=not query.strip()):
        try:
            results = st.session_state.retriever.search(query, top_k)
            with st.spinner("Generating grounded multilingual answer..."):
                answer = generate_answer(query, results, OllamaClient(model, host), answer_language)
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Retrieved sources")
            if results:
                st.dataframe(format_sources(results), use_container_width=True)
                with st.expander("Retrieved text passages"):
                    for r in results:
                        st.markdown(f"**{r['source']}** · score {r['score']:.3f}")
                        st.write(r["text"])
            else:
                st.warning("No matching text chunks found. Try a different query or check the uploaded documents.")
        except Exception as exc:
            st.error(str(exc))
else:
    st.info("Upload and index documents to begin. Example files are in the examples/ folder.")
