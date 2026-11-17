import streamlit as st
from core.pipeline import solve_problem
from database import initialize_db, save_run, list_runs

st.set_page_config(page_title="Multi-Step Reasoning AI", page_icon="🧠", layout="wide")
initialize_db()
st.title("Multi-Step Reasoning AI System")
st.caption("சிக்கலான கேள்வியை சிறு பணிகளாகப் பிரித்து, ஒவ்வொன்றையும் Local LLM மூலம் தீர்த்து, முடிவைச் சரிபார்க்கும் பயன்பாடு.")

with st.sidebar:
    st.subheader("அமைப்புகள்")
    max_steps = st.slider("அதிகபட்ச துணைப் பணிகள்", 2, 8, 5)
    max_revisions = st.slider("சரிபார்ப்பு / திருத்த முயற்சிகள்", 0, 3, 1)
    st.info("இந்த அமைப்பு சுருக்கமான விளக்கப் படிகளை வழங்கும்; தனிப்பட்ட மறை reasoning trace-ஐ வெளியிடாது.")

problem = st.text_area("சிக்கல் / கேள்வி", height=160, placeholder="உதா: ஒரு சிறிய நூலகத்திற்கான புத்தகக் கடன் மேலாண்மை அமைப்பை வடிவமைக்கவும்.")
context = st.text_area("கூடுதல் Context (விருப்பத்தேர்வு)", height=100)

if st.button("பகுத்து தீர்வு உருவாக்கு", type="primary"):
    if not problem.strip():
        st.warning("முதலில் ஒரு சிக்கலை உள்ளிடவும்.")
    else:
        try:
            with st.spinner("சிக்கலைப் பகுத்து துணைப் பணிகளைத் தீர்க்கிறது..."):
                result = solve_problem(problem.strip(), context.strip(), max_steps, max_revisions)
            st.subheader("சிக்கல் பகுப்பாய்வு")
            st.write(result["problem_summary"])
            st.subheader("துணைப் பணிகள்")
            for i, item in enumerate(result["steps"], 1):
                with st.expander(f'{i}. {item["task"]}', expanded=True):
                    st.write(item["answer"])
                    st.caption("நிலை: " + item["status"])
            st.subheader("இறுதி ஒருங்கிணைந்த தீர்வு")
            st.write(result["final_answer"])
            st.subheader("சரிபார்ப்பு")
            st.write(result["verification"])
            st.metric("மொத்த துணைப் பணிகள்", len(result["steps"]))
            save_run(problem, result)
        except Exception as exc:
            st.error(f"பிழை: {exc}")

st.divider()
st.subheader("முந்தைய செயல்பாடுகள்")
for row in list_runs():
    with st.expander(f"{row[0]} — {row[1][:100]}"):
        st.write("இறுதி தீர்வு:", row[2])
