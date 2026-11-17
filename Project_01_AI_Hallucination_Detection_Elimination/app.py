import streamlit as st
from core.pipeline import verify_and_correct
from core.knowledge_base import KnowledgeBase
from database import initialize_database, save_report, get_reports

st.set_page_config(page_title="AI Hallucination Detector", page_icon="🛡️", layout="wide")
initialize_database()

st.title("AI Hallucination Detection & Evidence-Based Correction")
st.caption("Local LLM + document retrieval. Paid API keys are not required.")

with st.sidebar:
    st.header("Knowledge Base")
    uploaded = st.file_uploader("Reference TXT / MD files", type=["txt", "md"], accept_multiple_files=True)
    st.info("சரிபார்ப்புக்கு உங்கள் நம்பகமான ஆதார ஆவணங்களைப் பதிவேற்றவும். ஆதாரம் இல்லாதபோது அமைப்பு UNKNOWN எனத் தெரிவிக்க வேண்டும்.")

documents = []
if uploaded:
    for file in uploaded:
        try:
            content = file.getvalue().decode("utf-8")
            documents.append({"source": file.name, "text": content})
        except UnicodeDecodeError:
            st.error(f"{file.name}: UTF-8 text ஆக வாசிக்க முடியவில்லை.")

question = st.text_area("கேள்வி / User question", placeholder="உதா: Who invented the telephone?")
answer = st.text_area("சரிபார்க்க வேண்டிய AI பதில் / AI-generated answer", height=160)
extra_context = st.text_area("கூடுதல் ஆதாரம் / Context (விருப்பத்தேர்வு)", height=100)

if st.button("சரிபார்த்து திருத்து", type="primary"):
    if not question.strip() or not answer.strip():
        st.warning("கேள்வி மற்றும் சரிபார்க்க வேண்டிய பதில் இரண்டும் தேவை.")
    else:
        try:
            with st.spinner("Claims பிரித்தெடுத்து ஆதாரங்களைச் சரிபார்க்கிறது..."):
                kb = KnowledgeBase(documents)
                result = verify_and_correct(
                    question=question.strip(),
                    answer=answer.strip(),
                    knowledge_base=kb,
                    extra_context=extra_context.strip()
                )
            st.subheader("முடிவு")
            st.metric("நிலை", result["overall_status"])
            st.write("**சுருக்கம்:**", result["summary"])
            st.subheader("Claim-level verification")
            for idx, item in enumerate(result["claims"], start=1):
                with st.expander(f'Claim {idx}: {item["claim"]}', expanded=True):
                    st.write("**நிலை:**", item["status"])
                    st.write("**விளக்கம்:**", item["reason"])
                    st.write("**ஆதாரம்:**")
                    for ev in item.get("evidence", []):
                        st.write(f'- {ev["source"]}: {ev["text"]}')
            st.subheader("திருத்தப்பட்ட பதில்")
            st.write(result["corrected_answer"])
            st.caption("திருத்தம் ஆதாரங்களால் உறுதிப்படுத்தப்படாத இடங்களில் uncertainty குறிப்பிடப்பட வேண்டும்.")
            save_report(question, answer, result)
        except Exception as exc:
            st.error(f"செயல்பாட்டு பிழை: {exc}")

st.divider()
st.subheader("முந்தைய சரிபார்ப்பு அறிக்கைகள்")
for report in get_reports():
    with st.expander(f'{report[0]} — {report[1][:90]}'):
        st.write("நிலை:", report[2])
        st.write("திருத்தப்பட்ட பதில்:", report[3])
