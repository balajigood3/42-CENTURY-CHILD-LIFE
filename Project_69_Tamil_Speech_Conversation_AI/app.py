import streamlit as st
from speech_ai.speech import transcribe_audio, synthesize_speech
from speech_ai.dialogue import chat_local
from speech_ai.history import append_turn, read_turns

st.set_page_config(page_title="Tamil Speech Conversation AI", layout="wide")
st.title("தமிழ் குரல் உரையாடல் AI")
st.caption("Local speech recognition + local LLM conversation + optional speech output. Paid API key தேவையில்லை.")

model = st.text_input("Ollama model", "qwen2.5:3b")
whisper_model = st.selectbox("Speech recognition model", ["tiny", "base", "small"], index=2)
input_mode = st.radio("Input method", ["Audio upload", "Text input"], horizontal=True)

user_text = ""
if input_mode == "Audio upload":
    audio = st.file_uploader("உங்கள் குரல் பதிவை பதிவேற்றவும்", type=["wav", "mp3", "m4a", "webm", "ogg"])
    language = st.selectbox("Audio language", ["ta", "en", "hi", "te", "ml", "kn"], index=0)
    if audio and st.button("குரலை உரையாக மாற்று"):
        try:
            user_text = transcribe_audio(audio.getvalue(), audio.name, whisper_model, language)
            st.session_state["transcribed_text"] = user_text
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    user_text = st.text_area("அடையாளம் காணப்பட்ட உரை (திருத்தலாம்)",
                             value=st.session_state.get("transcribed_text", ""), height=120)
else:
    user_text = st.text_area("உங்கள் செய்தி", height=120, placeholder="வணக்கம், இன்று எப்படி இருக்கிறீர்கள்?")

if st.button("பதிலளி", type="primary", disabled=not user_text.strip()):
    try:
        history = st.session_state.get("chat_history", [])
        answer = chat_local(user_text, history, model=model)
        st.session_state.setdefault("chat_history", []).extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": answer}
        ])
        append_turn("data/conversation.jsonl", user_text, answer)
        st.session_state["last_answer"] = answer
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

if st.session_state.get("last_answer"):
    st.subheader("AI பதில்")
    st.markdown(st.session_state["last_answer"])
    if st.button("பதிலை Audio-ஆக உருவாக்கு"):
        try:
            audio_path = synthesize_speech(st.session_state["last_answer"], "data/response.wav")
            st.audio(audio_path)
        except (ValueError, RuntimeError) as exc:
            st.warning(str(exc))
with st.expander("உரையாடல் வரலாறு"):
    for turn in reversed(read_turns("data/conversation.jsonl", 20)):
        st.markdown(f"**நீங்கள்:** {turn['user']}")
        st.markdown(f"**AI:** {turn['assistant']}")
