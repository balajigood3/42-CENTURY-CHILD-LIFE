import json
import streamlit as st
from PIL import Image
from video_understanding.processor import inspect_video, caption_frames
from video_understanding.summarizer import summarize_video

st.set_page_config(page_title="Video Understanding & Summary AI", page_icon="🎬", layout="wide")
st.title("Video Understanding & Summary AI")
st.caption("Inspect video metadata and sampled keyframes locally. Optional BLIP captioning; no paid API keys.")
upload = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv", "webm"])
max_frames = st.slider("Maximum keyframes to sample", 1, 12, 6)
use_blip = st.checkbox("Enable optional local BLIP frame captioning", value=False,
                       help="Requires transformers + torch and model weights; first run may download them.")
transcript = st.text_area("Optional audio transcript (paste if available)", height=100)
if upload and st.button("Analyze video", type="primary"):
    try:
        data = upload.getvalue()
        with st.spinner("Inspecting video and sampling keyframes..."):
            result = inspect_video(upload.name, data, max_frames)
            for item in result["sampled_frames"]:
                st.image(Image.fromarray(item["frame"]), caption=f"Keyframe at {item['timestamp']:.1f}s", width=300)
            caption_result = caption_frames(result["sampled_frames"], use_blip)
            report = summarize_video(result, caption_result["captions"], transcript)
        if caption_result["note"]:
            st.info(caption_result["note"])
        st.subheader("Video summary")
        st.write(report["summary"])
        st.json({k: v for k, v in report.items() if k != "summary"})
        st.download_button("Download summary JSON", json.dumps(report, indent=2), "video-summary.json", "application/json")
        st.download_button("Download summary TXT", report["summary"], "video-summary.txt", "text/plain")
    except Exception as exc:
        st.error(str(exc))
elif not upload:
    st.info("Upload a supported video file to begin.")
