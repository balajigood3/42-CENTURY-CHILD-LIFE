import hashlib, json
import streamlit as st
from app.core import OllamaClient, extract_graph, build_graph, answer_query, export_graph
from app.storage import GraphStore

st.set_page_config(page_title="Dynamic Knowledge Graph RAG", layout="wide")
st.title("Dynamic Knowledge Graph RAG")
st.caption("Build and update a local entity-relation graph from documents, then retrieve connected evidence.")
with st.sidebar:
    model = st.text_input("Ollama model", "qwen2.5:3b")
    host = st.text_input("Ollama host", "http://localhost:11434")
    st.info("Local Ollama inference; no paid API key.")
store = GraphStore()
uploads = st.file_uploader("Add TXT / Markdown documents", type=["txt", "md"], accept_multiple_files=True)
if st.button("Ingest / Update graph", type="primary", disabled=not uploads):
    client = OllamaClient(model, host)
    progress = st.progress(0)
    for i, f in enumerate(uploads):
        raw = f.getvalue()
        digest = hashlib.sha256(raw).hexdigest()
        existing = {n for n, _ in store.load_all()}
        # Re-extract on every explicit upload to support document updates.
        with st.spinner(f"Extracting graph from {f.name}..."):
            doc_graph = extract_graph(raw.decode("utf-8", errors="replace"), f.name, client)
            store.upsert(f.name, digest, doc_graph)
        progress.progress((i + 1) / len(uploads))
    st.success("Knowledge graph updated.")

records = store.load_all()
if records:
    graphs = [g for _, g in records]
    graph = build_graph(graphs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", len(records))
    c2.metric("Entities", graph.number_of_nodes())
    c3.metric("Relations", graph.number_of_edges())
    with st.expander("Current graph contents"):
        st.write("Documents:", ", ".join(n for n, _ in records))
        st.json({"entities": [{"id": n, **d} for n, d in graph.nodes(data=True)],
                 "relations": [{"source": u, "target": v, **d} for u, v, d in graph.edges(data=True)]})
    question = st.text_input("Ask a question about the knowledge graph")
    if st.button("Retrieve and answer", disabled=not question.strip()):
        try:
            with st.spinner("Retrieving connected graph evidence and generating answer..."):
                answer, sub = answer_query(question, graph, OllamaClient(model, host))
            st.subheader("Answer")
            st.write(answer)
            st.subheader("Retrieved subgraph")
            st.write(f"{len(sub['nodes'])} entities · {len(sub['edges'])} relations")
            st.json(sub)
        except Exception as e:
            st.error(str(e))
    if st.button("Export full graph as GraphML"):
        path = "data/knowledge_graph.graphml"
        export_graph(graph, path)
        with open(path, "rb") as f:
            st.download_button("Download GraphML", f, "knowledge_graph.graphml")
else:
    st.info("Upload at least one TXT or Markdown file to create the initial graph.")
