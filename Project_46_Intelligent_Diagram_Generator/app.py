import streamlit as st
from diagram_engine import parse_process, render_svg, to_mermaid

st.set_page_config(page_title="Intelligent Diagram Generator", page_icon="🧩", layout="wide")
st.title("Intelligent Diagram Generator")
st.caption("Convert plain-language process steps into editable Mermaid and downloadable SVG diagrams. No paid API keys.")

example = "User submits request\nValidate request\nIf valid -> Process request\nIf invalid -> Show error\nSend confirmation"
description = st.text_area("Describe your process (one step per line; use A -> B for explicit connections)",
                           value=example, height=220)
diagram_type = st.selectbox("Diagram layout", ["Flowchart", "Sequence of steps"])
if st.button("Generate diagram", type="primary", disabled=not description.strip()):
    try:
        nodes, edges = parse_process(description, diagram_type)
        svg = render_svg(nodes, edges, title="Generated Process Diagram")
        mermaid = to_mermaid(nodes, edges)
        st.session_state["diagram_svg"] = svg
        st.session_state["diagram_mermaid"] = mermaid
        st.session_state["diagram_nodes"] = nodes
        st.success(f"Generated diagram with {len(nodes)} nodes and {len(edges)} connections.")
    except ValueError as exc:
        st.error(str(exc))

if "diagram_svg" in st.session_state:
    st.subheader("Diagram preview")
    st.components.v1.html(st.session_state["diagram_svg"], height=520, scrolling=True)
    st.download_button("Download SVG", st.session_state["diagram_svg"],
                       file_name="process_diagram.svg", mime="image/svg+xml")
    st.subheader("Mermaid source")
    st.code(st.session_state["diagram_mermaid"], language="mermaid")
    st.download_button("Download Mermaid", st.session_state["diagram_mermaid"],
                       file_name="process_diagram.mmd", mime="text/plain")
    st.write("**Detected nodes**")
    st.write([node["label"] for node in st.session_state["diagram_nodes"]])
