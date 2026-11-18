import json
import streamlit as st
from story_generator.vision import describe_image, validate_image
from story_generator.story import generate_story

st.set_page_config(page_title="Image-to-Story Generator", page_icon="📖", layout="wide")
st.title("Image-to-Story Generator")
st.caption("Turn an image into a short story using local processing. No paid API key required.")
upload = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
style = st.selectbox("Story style", ["adventure", "fairy_tale", "science_fiction", "mystery"])
direction = st.text_input("Optional story direction", "Make the main character discover something unexpected.")
use_blip = st.checkbox("Use optional local BLIP image captioning model", value=False,
                       help="Requires transformers + torch and model weights. First use may download weights.")
if upload and st.button("Generate story", type="primary"):
    try:
        data = upload.getvalue()
        image = validate_image(data)
        st.image(image, caption=f"Uploaded image · {image.width} × {image.height}")
        with st.spinner("Analyzing image and writing story..."):
            details = describe_image(data, use_blip=use_blip)
            st.write("Image description:", details["caption"])
            if details["note"]:
                st.info(details["note"])
            story = generate_story(details["caption"], style, direction)
        st.subheader(story["title"])
        st.write(story["story"])
        st.caption(f"{story['word_count']} words · {story['generation_method']}")
        st.download_button("Download story JSON", json.dumps({"image": details, "story": story}, indent=2),
                           "image-story.json", "application/json")
        st.download_button("Download story TXT", story["story"], "image-story.txt", "text/plain")
    except Exception as exc:
        st.error(str(exc))
elif not upload:
    st.info("Upload a JPEG, PNG, or WEBP image to begin.")
