import json
import streamlit as st
from multimodal_assistant.processors import (
    validate_upload, process_text, process_pdf, process_image, process_audio, build_response
)

st.set_page_config(page_title="Universal Multimodal Assistant", page_icon="🧠", layout="wide")
st.title("Universal Multimodal Assistant")
st.caption("Local text, PDF, image and audio intake. No paid API key or hosted model required.")
typed = st.text_area("Ask or paste text", height=130, placeholder="Enter a question or text to analyze...")
upload = st.file_uploader("Or upload a file", type=["txt","md","csv","json","yaml","yml","pdf","png","jpg","jpeg","webp","bmp","wav","mp3","m4a","ogg","flac"])
if st.button("Process input", type="primary"):
    try:
        if upload:
            data = upload.getvalue()
            kind = validate_upload(upload.name, data)
            if kind == "text":
                extracted = process_text(data)
                result = build_response(extracted, kind)
                st.text_area("Extracted text", extracted, height=180)
            elif kind == "pdf":
                extracted = process_pdf(data)
                result = build_response(extracted, kind)
                st.text_area("Extracted PDF text", extracted, height=220)
            elif kind == "image":
                details = process_image(data)
                result = build_response(details.get("extracted_text", ""), kind)
                st.image(data, caption=f"{details['width']} × {details['height']} · {details['format']}")
                st.json(details)
            else:
                details = process_audio(data, upload.name)
                result = build_response(details.get("transcript", ""), kind)
                st.json(details)
        else:
            result = build_response(typed, "text")
        st.subheader("Assistant result")
        st.json(result)
        st.download_button("Download result JSON", json.dumps(result, indent=2), "multimodal-result.json", "application/json")
    except Exception as exc:
        st.error(str(exc))
