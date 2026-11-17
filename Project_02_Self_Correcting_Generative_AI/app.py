import streamlit as st
from core.pipeline import run_pipeline
from database import initialize_database, save_history, get_history

st.set_page_config(page_title="Self-Correcting Generative AI", page_icon="🤖", layout="wide")
initialize_database()

st.title("Self-Correcting Generative AI")
st.caption("Local LLM மூலம் பதிலை உருவாக்கி, மதிப்பீடு செய்து, தேவையானால் திருத்தும் செயலி.")

question = st.text_area("உங்கள் கேள்வி", height=110, placeholder="உதா: Explain the difference between AI and ML.")
context = st.text_area("ஆதாரத் தகவல் / Context (விருப்பத்தேர்வு)", height=130)

if st.button("பதிலை உருவாக்கி சரிபார்க்கவும்", type="primary"):
    if not question.strip():
        st.warning("முதலில் கேள்வியை உள்ளிடவும்.")
    else:
        try:
            with st.spinner("Local LLM பதிலை உருவாக்கி மதிப்பீடு செய்கிறது..."):
                result = run_pipeline(question.strip(), context.strip())
            st.subheader("ஆரம்ப பதில்")
            st.write(result["initial_answer"])
            st.subheader("இறுதி பதில்")
            st.write(result["final_answer"])
            st.subheader("மதிப்பீட்டு அறிக்கை")
            st.metric("மதிப்பீட்டு Score", f'{result["evaluation"]["score"]}/100')
            st.write("நிலை:", result["evaluation"]["status"])
            st.code(result["evaluation"]["details"])
            st.subheader("திருத்த வரலாறு")
            for item in result["history"]:
                with st.expander(f'முயற்சி {item["iteration"]} — {item["status"]}'):
                    st.write(item["answer"])
                    st.write(f'Score: {item["score"]}/100')
            save_history(question, result["initial_answer"], result["final_answer"],
                         result["evaluation"]["score"], result["evaluation"]["status"])
        except Exception as exc:
            st.error(f"செயல்பாட்டு பிழை: {exc}")

st.divider()
st.subheader("முந்தைய முடிவுகள்")
for row in get_history():
    with st.expander(f"கேள்வி: {row[1]}"):
        st.write("ஆரம்ப பதில்:", row[2])
        st.write("இறுதி பதில்:", row[3])
        st.write("Score:", row[4], "| Status:", row[5])
