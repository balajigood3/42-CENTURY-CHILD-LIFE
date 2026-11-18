import streamlit as st
from core.detector import detect_contradictions
from database import init_db, save_result, get_history
st.set_page_config(page_title="AI Contradiction Detector", page_icon="⚖️", layout="wide")
init_db()
st.title("AI Contradiction Detection System")
st.caption("பல உரைகள் அல்லது ஆவணங்களில் உள்ள முரண்பட்ட கூற்றுகளை Local LLM மூலம் கண்டறிதல்.")
st.info("குறைந்தது இரண்டு ஆதாரங்களை ஒப்பிடவும். ஆதாரம் தெளிவாக இல்லாதபோது UNKNOWN என வகைப்படுத்தப்படும்.")
a,b=st.columns(2)
with a:
    an=st.text_input("முதல் ஆதாரத்தின் பெயர்","Source A")
    at=st.text_area("முதல் உரை",height=220)
with b:
    bn=st.text_input("இரண்டாவது ஆதாரத்தின் பெயர்","Source B")
    bt=st.text_area("இரண்டாவது உரை",height=220)
objective=st.text_input("விருப்பமான ஒப்பீட்டு நோக்கம்")
if st.button("முரண்பாடுகளை கண்டறி",type="primary"):
    if not at.strip() or not bt.strip(): st.warning("இரண்டு ஆதாரங்களிலும் உரை தேவை.")
    else:
        try:
            with st.spinner("கூற்றுகளைப் பிரித்து ஒப்பிடுகிறது..."):
                result=detect_contradictions({"name":an,"text":at},{"name":bn,"text":bt},objective)
            st.subheader("முடிவு")
            st.metric("மொத்த நிலை",result["overall_status"])
            st.write(result["summary"])
            for i,item in enumerate(result["comparisons"],1):
                with st.expander(f'{i}. {item["topic"]} — {item["status"]}',expanded=True):
                    st.write(f'**{an}:** {item["source_a_claim"]}')
                    st.write(f'**{bn}:** {item["source_b_claim"]}')
                    st.write("**விளக்கம்:**",item["explanation"])
                    st.write("**பரிந்துரை:**",item["resolution"])
            st.subheader("முழு அறிக்கை")
            st.json(result)
            save_result(an,bn,result)
        except Exception as e: st.error(f"செயல்பாட்டு பிழை: {e}")
st.divider()
st.subheader("முந்தைய அறிக்கைகள்")
for row in get_history():
    with st.expander(f"{row[0]} — {row[1]} vs {row[2]}"):
        st.write("நிலை:",row[3]); st.write(row[4])
