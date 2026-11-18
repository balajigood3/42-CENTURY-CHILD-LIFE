import streamlit as st
from presentation_builder import parse_outline, create_presentation

st.set_page_config(page_title="AI Presentation Generator", page_icon="📊", layout="wide")
st.title("AI Presentation Generator")
st.caption("Create editable PowerPoint presentations from a structured text outline. No paid API keys.")

default_outline = """# Generative AI: An Overview
## What is Generative AI?
- AI that creates new content
- Works with text, images, audio and code
## How does it work?
- Learns patterns from training data
- Generates outputs from prompts
## Common applications
- Content creation
- Software development
- Research assistance
## Benefits and risks
- Faster workflows and creativity
- Requires verification and responsible use
## Key takeaways
- Start with a clear use case
- Evaluate quality, safety and cost"""

with st.sidebar:
    st.header("Presentation settings")
    author = st.text_input("Author / organization", "Created with AI Presentation Generator")
    theme = st.selectbox("Theme", ["Professional Blue", "Modern Dark", "Minimal Light"])
    include_agenda = st.checkbox("Add agenda slide", value=True)
    include_closing = st.checkbox("Add closing slide", value=True)

outline = st.text_area("Presentation outline", value=default_outline, height=360,
                       help="Use # for the title, ## for slide titles, and - for bullet points.")
try:
    slides = parse_outline(outline, include_agenda=include_agenda, include_closing=include_closing)
    st.caption(f"Preview: {len(slides)} slides")
    for idx, slide in enumerate(slides, 1):
        with st.expander(f"{idx}. {slide['title']}"):
            for bullet in slide["bullets"]:
                st.write(f"• {bullet}")
except ValueError as exc:
    st.error(str(exc))
    slides = []

if st.button("Generate PowerPoint", type="primary", disabled=not slides):
    try:
        pptx_bytes = create_presentation(slides, author=author, theme=theme)
        st.session_state["pptx_bytes"] = pptx_bytes
        st.success("Editable PowerPoint generated.")
    except Exception as exc:
        st.error(f"Presentation generation failed: {exc}")

if "pptx_bytes" in st.session_state:
    st.download_button("Download PowerPoint (.pptx)", st.session_state["pptx_bytes"],
                       file_name="generated_presentation.pptx",
                       mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
