import streamlit as st
from core.pipeline import analyze_uncertainty
from database import init_db, save_analysis, get_history

st.set_page_config(page_title="Uncertainty-Aware Generative AI", page_icon="🎯", layout="wide")
init_db()
st.title("Uncertainty-Aware Generative AI System")
st.caption("தகவல் போதாமை, ambiguity மற்றும் confidence வரம்புகளை வெளிப்படையாகக் காட்டும் Local LLM பயன்பாடு.")
question = st.text_area("உங்கள் கேள்வி", height=120)
context = st.text_area("கிடைக்கும் தகவல் / ஆதாரங்கள் (விருப்பத்தேர்வு)", height=180)
if st.button("பதில் மற்றும் Uncertainty மதிப்பீடு", type="primary"):
    if not question.strip():
        st.warning("கேள்வியை உள்ளிடவும்.")
    else:
        try:
            with st.spinner("பதில் உருவாக்கி uncertainty-ஐ பகுப்பாய்வு செய்கிறது..."):
                result = analyze_uncertainty(question.strip(), context.strip())
            st.subheader("AI பதில்")
            st.write(result["answer"])
            st.subheader("Uncertainty அறிக்கை")
            st.metric("Uncertainty நிலை", result["uncertainty_level"])
            for title, key in [("காரணங்கள்", "uncertainty_reasons"), ("கருதுகோள்கள்", "assumptions"), ("மேலும் தேவைப்படும் தகவல்கள்", "missing_information")]:
                st.write(f"**{title}:**")
                for item in result[key]:
                    st.write(f"- {item}")
            st.write("**Confidence explanation:**", result["confidence_explanation"])
            st.info("இந்த நிலை qualitative self-assessment மட்டுமே; calibrated probability அல்லது factual guarantee அல்ல.")
            save_analysis(question, result)
        except Exception as exc:
            st.error(f"பிழை: {exc}")
st.divider()
st.subheader("முந்தைய மதிப்பீடுகள்")
for row in get_history():
    with st.expander(f"{row[0]} — {row[1][:90]}"):
        st.write("Uncertainty:", row[2])
        st.write(row[3])
