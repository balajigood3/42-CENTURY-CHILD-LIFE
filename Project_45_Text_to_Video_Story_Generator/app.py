import streamlit as st
from story_video import parse_story, render_video, DEFAULT_WIDTH, DEFAULT_HEIGHT

st.set_page_config(page_title="Text-to-Video Story Generator", page_icon="🎬", layout="wide")
st.title("Text-to-Video Story Generator")
st.caption("Turn a written story into a narrated-style scene video with title cards and captions. No paid API keys.")

story = st.text_area(
    "Enter your story",
    value=("A young inventor finds a mysterious map. She follows its clues through an old forest. "
           "At the final landmark, she discovers a forgotten library and begins a new adventure."),
    height=180
)
col1, col2, col3 = st.columns(3)
with col1:
    title = st.text_input("Video title", "The Hidden Map")
with col2:
    seconds = st.slider("Seconds per scene", 2, 8, 4)
with col3:
    style = st.selectbox("Visual style", ["Midnight", "Sunrise", "Forest", "Ocean"])

if st.button("Generate video", type="primary", disabled=not story.strip()):
    try:
        scenes = parse_story(story, max_scenes=8)
        with st.spinner("Rendering MP4 video…"):
            output = render_video(scenes, title=title, seconds_per_scene=seconds, style=style)
        st.session_state["video_bytes"] = output
        st.session_state["scene_list"] = scenes
        st.success(f"Video generated with {len(scenes)} scenes.")
    except Exception as exc:
        st.error(f"Could not generate video: {exc}")

if "scene_list" in st.session_state:
    st.subheader("Storyboard")
    for index, scene in enumerate(st.session_state["scene_list"], 1):
        st.write(f"**Scene {index}:** {scene}")
if "video_bytes" in st.session_state:
    st.video(st.session_state["video_bytes"])
    st.download_button("Download MP4", st.session_state["video_bytes"],
                       file_name="generated_story.mp4", mime="video/mp4")
