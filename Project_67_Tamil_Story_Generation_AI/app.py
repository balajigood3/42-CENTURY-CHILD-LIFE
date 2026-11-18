import streamlit as st
from story_ai.generator import GENRE_TEMPLATES, generate_story
from story_ai.storage import save_story, recent_stories

st.set_page_config(page_title="Tamil Story Generation AI", page_icon="📖", layout="wide")
st.title("தமிழ் கதை உருவாக்கும் AI")
st.caption("Tamil Story Generation AI · Local-first · No paid API key")
topic = st.text_input("கதையின் கருப்பொருள்", placeholder="எ.கா. சுற்றுச்சூழலைக் காப்பாற்றும் சிறுமி")
genre = st.selectbox("கதை வகை", list(GENRE_TEMPLATES))
audience = st.selectbox("யாருக்கான கதை?", ["குழந்தைகள்", "இளைஞர்கள்", "அனைவரும்"])
length = st.selectbox("கதை நீளம்", ["சிறியது", "நடுத்தரம்", "நீளமானது"])
mode_label = st.radio("உருவாக்கும் முறை", ["Offline sample", "Local Ollama model"], horizontal=True)
mode = "ollama" if mode_label == "Local Ollama model" else "template"
model = st.text_input("Ollama model", "qwen2.5:3b", disabled=(mode == "template"))
if st.button("கதை உருவாக்கு", type="primary", disabled=not topic.strip()):
    try:
        story = generate_story(topic, genre, audience, length, mode=mode, model=model)
        st.session_state["generated_story"] = story
        save_story("data/stories.jsonl", topic, genre, story, mode)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
if st.session_state.get("generated_story"):
    st.subheader("உங்கள் கதை")
    st.markdown(st.session_state["generated_story"])
    st.download_button("கதையைப் பதிவிறக்கு", st.session_state["generated_story"],
                       file_name="tamil_story.md", mime="text/markdown")
with st.expander("முந்தைய கதைகள்"):
    for item in reversed(recent_stories("data/stories.jsonl")):
        st.markdown(f"**{item['topic']} · {item['genre']}**")
        st.markdown(item["story"])
