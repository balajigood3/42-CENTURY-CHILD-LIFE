import streamlit as st
from PIL import Image
from multimodal_assistant import (
    validate_upload, image_context, transcribe_audio, build_response
)

st.set_page_config(page_title="Real-Time Multimodal AI Assistant", page_icon="🤖", layout="wide")
st.title("Real-Time Multimodal AI Assistant")
st.caption("Interact with text, images and audio in one local-first workspace. No paid API keys.")

with st.sidebar:
    st.header("Local model options")
    use_blip = st.checkbox("Enable optional BLIP image understanding", value=False)
    use_whisper = st.checkbox("Enable optional Whisper audio transcription", value=False)
    st.caption("Optional model weights download on first use. Basic mode works without model downloads.")

text_context = st.text_area("Text context or notes", height=130,
                            placeholder="Paste notes, instructions, or background context…")
image_file = st.file_uploader("Add an image", type=["png", "jpg", "jpeg", "webp", "bmp"])
audio_file = st.file_uploader("Add audio", type=["wav", "mp3", "m4a", "ogg", "flac"])
question = st.text_input("Ask the assistant", placeholder="Summarize the provided information…")

if image_file:
    st.image(image_file, caption="Uploaded image", use_container_width=True)
if audio_file:
    st.audio(audio_file)

if st.button("Process multimodal request", type="primary", disabled=not question.strip()):
    try:
        contexts = []
        if text_context.strip():
            contexts.append(("Text", text_context.strip()))
        if image_file:
            validate_upload(image_file.name, image_file.size, "image")
            img = Image.open(image_file).convert("RGB")
            contexts.append(("Image", image_context(img, use_blip=use_blip)))
        if audio_file:
            validate_upload(audio_file.name, audio_file.size, "audio")
            if use_whisper:
                transcript = transcribe_audio(audio_file.getvalue(), audio_file.name)
                contexts.append(("Audio transcript", transcript or "No speech detected."))
            else:
                contexts.append(("Audio", "Audio file attached. Enable Whisper transcription to extract spoken content."))
        if not contexts:
            contexts.append(("Text", "No additional context was provided."))
        result = build_response(question, contexts)
        st.session_state["multimodal_result"] = result
    except Exception as exc:
        st.error(f"Unable to process request: {exc}")

if "multimodal_result" in st.session_state:
    result = st.session_state["multimodal_result"]
    st.subheader("Assistant response")
    st.write(result["response"])
    st.caption(result["mode_note"])
    with st.expander("Inspect combined context"):
        for item in result["context"]:
            st.markdown(f"**{item['modality']}**")
            st.write(item["content"])
    st.download_button(
        "Download response as Markdown",
        result["markdown"],
        file_name="multimodal_response.md",
        mime="text/markdown",
    )
