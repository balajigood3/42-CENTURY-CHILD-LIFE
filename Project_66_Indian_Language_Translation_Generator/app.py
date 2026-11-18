import streamlit as st
from indic_translate.engine import LANGUAGES, translate
from indic_translate.text_utils import split_text, estimate_word_count
from indic_translate.history import save_translation, load_history

st.set_page_config(page_title="Indian Language Translation Generator", layout="wide")
st.title("Indian Language Translation Generator")
st.caption("இந்திய மொழிகளுக்கிடையே local / offline translation workflow.")
source = st.selectbox("Source language", list(LANGUAGES), index=0)
target = st.selectbox("Target language", list(LANGUAGES), index=1)
use_argos = st.checkbox("Use installed Argos Translate model", value=False)
text = st.text_area("Input text", height=180, placeholder="Enter text to translate...")
if st.button("Translate", type="primary", disabled=not text.strip()):
    try:
        chunks = split_text(text)
        outputs = [translate(chunk, source, target, use_argos=use_argos) for chunk in chunks]
        result = "\n".join(outputs)
        st.subheader("Translation output")
        st.text_area("Translated text", result, height=220)
        st.caption(f"Input words: {estimate_word_count(text)} | Chunks: {len(chunks)}")
        save_translation("data/history.jsonl", text, result, source, target)
        st.download_button("Download translation", result, "translation.txt")
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
with st.expander("Translation history"):
    for row in reversed(load_history("data/history.jsonl", 10)):
        st.markdown(f"**{row['source_language']} → {row['target_language']}**")
        st.write(row["source_text"])
        st.write(row["translated_text"])
