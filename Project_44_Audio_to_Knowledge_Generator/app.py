import json
import streamlit as st
from audio_knowledge import validate_audio, transcribe_audio, build_knowledge, MAX_BYTES

st.set_page_config(page_title="Audio-to-Knowledge Generator", page_icon="🎧", layout="wide")
st.title("Audio-to-Knowledge Generator")
st.caption("Local-first audio transcription and structured knowledge extraction — no paid API keys.")

with st.sidebar:
    st.header("Transcription")
    model_size = st.selectbox("Whisper model", ["tiny", "base", "small"], index=0)
    st.caption("The model is downloaded by faster-whisper on first use. Tiny is recommended for a quick start.")
    st.write(f"Maximum upload: {MAX_BYTES // (1024 * 1024)} MB")

uploaded = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg", "flac"])
transcript = st.text_area("Transcript (you can edit or paste text here)", height=240,
                           placeholder="Transcribe an audio file or paste an existing transcript…")

if uploaded is not None:
    try:
        validate_audio(uploaded.name, uploaded.size)
        if st.button("Transcribe audio", type="primary"):
            with st.spinner("Loading local speech model and transcribing…"):
                result = transcribe_audio(uploaded.getvalue(), uploaded.name, model_size)
            st.session_state["transcript"] = result
            st.success("Transcription completed. Review and edit the transcript below.")
    except ValueError as exc:
        st.error(str(exc))
    except RuntimeError as exc:
        st.error(str(exc))

if "transcript" in st.session_state and not transcript:
    transcript = st.session_state["transcript"]

if st.button("Generate knowledge", disabled=not bool(transcript.strip())):
    st.session_state["knowledge"] = build_knowledge(transcript)

if "knowledge" in st.session_state:
    data = st.session_state["knowledge"]
    st.subheader("Generated knowledge")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Summary")
        st.write(data["summary"])
        st.markdown("### Key points")
        for item in data["key_points"]:
            st.write(f"• {item}")
        st.markdown("### Action items")
        for item in data["action_items"]:
            st.write(f"☐ {item}")
    with c2:
        st.markdown("### Terms and entities")
        st.write(", ".join(data["terms"]) or "No terms detected")
        st.markdown("### FAQ candidates")
        for item in data["faq_candidates"]:
            st.write(f"• {item}")
    st.download_button("Download JSON", json.dumps(data, ensure_ascii=False, indent=2),
                       file_name="audio_knowledge.json", mime="application/json")
    md = "# Audio Knowledge\n\n## Summary\n" + data["summary"] + "\n\n## Key points\n"
    md += "".join(f"- {x}\n" for x in data["key_points"])
    md += "\n## Action items\n" + "".join(f"- [ ] {x}\n" for x in data["action_items"])
    md += "\n## Terms\n" + ", ".join(data["terms"]) + "\n\n## FAQ candidates\n"
    md += "".join(f"- {x}\n" for x in data["faq_candidates"])
    st.download_button("Download Markdown", md, file_name="audio_knowledge.md", mime="text/markdown")
