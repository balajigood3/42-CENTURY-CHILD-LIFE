import streamlit as st
import tempfile
from pathlib import Path
from voice_knowledge.transcribe import transcribe_audio, TranscriptionError
from voice_knowledge.knowledge import create_knowledge_note, search_note
from voice_knowledge.storage import save_note, load_notes

st.set_page_config(page_title="Tamil Voice-to-Text Knowledge AI", layout="wide")
st.title("Tamil Voice-to-Text Knowledge AI")
st.caption("தமிழ் audio-வை text-ஆக மாற்றி, searchable knowledge notes உருவாக்குங்கள்.")
st.info("Local Whisper model first run-இல் model files download செய்யப்படலாம்; paid API key தேவையில்லை.")
upload = st.file_uploader("Tamil audio upload", type=["wav", "mp3", "m4a", "flac", "ogg"])
model = st.selectbox("Whisper model size", ["tiny", "base", "small"], index=1)
if upload and st.button("Transcribe audio", type="primary"):
    suffix = Path(upload.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(upload.getvalue())
        temp_path = temp.name
    try:
        with st.spinner("Audio transcribe செய்யப்படுகிறது..."):
            result = transcribe_audio(temp_path, model)
        st.subheader("Transcript")
        st.text_area("Tamil transcript", result["text"], height=180)
        note = create_knowledge_note(result["text"], Path(upload.name).stem)
        saved = save_note(note)
        st.success(f"Knowledge note saved: {saved.name}")
        st.write("**Keywords:**", ", ".join(note["keywords"]))
        st.write("**Key points:**")
        for point in note["key_points"]:
            st.write(f"- {point}")
    except TranscriptionError as exc:
        st.error(str(exc))
    except ValueError as exc:
        st.warning(str(exc))
    finally:
        Path(temp_path).unlink(missing_ok=True)

st.divider()
st.subheader("Search saved knowledge")
notes = load_notes()
if not notes:
    st.caption("Saved notes இல்லை. முதலில் audio upload செய்து transcribe செய்யுங்கள்.")
else:
    selected = st.selectbox("Choose note", notes, format_func=lambda n: n.get("source", "audio"))
    query = st.text_input("தேட வேண்டிய சொல் / கேள்வி")
    if st.button("Search note", disabled=not query.strip()):
        hits = search_note(selected, query)
        if hits:
            for hit in hits:
                st.write(hit["text"])
        else:
            st.info("பொருத்தமான வாக்கியம் கிடைக்கவில்லை.")
