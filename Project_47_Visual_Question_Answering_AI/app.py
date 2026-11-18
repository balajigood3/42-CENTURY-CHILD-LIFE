import streamlit as st
from PIL import Image
from visual_qa import validate_image, answer_question, MAX_IMAGE_BYTES

st.set_page_config(page_title="Visual Question Answering AI", page_icon="👁️", layout="wide")
st.title("Visual Question Answering AI")
st.caption("Ask questions about an image using an optional local vision-language model. No paid API keys.")

with st.sidebar:
    st.header("Model settings")
    mode = st.selectbox("Answering mode", ["Automatic", "Local BLIP model", "Basic image analysis"])
    st.caption("BLIP mode downloads model weights on first use and runs locally afterward.")
    st.write(f"Maximum image size: {MAX_IMAGE_BYTES // (1024 * 1024)} MB")

uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp", "bmp"])
question = st.text_input("Ask a question about the image",
                         placeholder="What is in this picture?")

if uploaded:
    try:
        validate_image(uploaded.name, uploaded.size)
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)
        if st.button("Answer question", type="primary", disabled=not question.strip()):
            with st.spinner("Analyzing image…"):
                result = answer_question(image, question, mode=mode)
            st.session_state["qa_result"] = result
    except Exception as exc:
        st.error(f"Image processing failed: {exc}")

if "qa_result" in st.session_state:
    result = st.session_state["qa_result"]
    st.subheader("Answer")
    st.write(result["answer"])
    st.caption(f"Method: {result['method']} · {result['confidence_note']}")
    if result.get("details"):
        with st.expander("Image details"):
            st.json(result["details"])
