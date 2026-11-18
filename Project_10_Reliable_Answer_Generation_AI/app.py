import streamlit as st
from src.pipeline import ReliableAnswerPipeline

st.set_page_config(page_title="Reliable Answer Generation AI",layout="wide")
st.title("Reliable Answer Generation AI")
st.caption("Evidence-aware local AI answer pipeline with uncertainty handling and deterministic checks.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    st.caption("Paid API key தேவையில்லை. `ollama pull qwen2.5:3b` இயக்கவும்.")
pipeline=ReliableAnswerPipeline(model,url)
question=st.text_area("கேள்வி",height=120)
evidence=st.text_area("ஆதாரம் / reference text (விருப்பம்)",height=180,
    placeholder="நம்பகமான பதில் உருவாக்க வேண்டிய ஆதாரத்தை இங்கே சேர்க்கவும்.")
if st.button("Reliable answer உருவாக்கு",type="primary"):
    if not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
    else:
        with st.spinner("Answer → verification → finalization..."):
            result=pipeline.run(question,evidence)
        st.subheader("இறுதி பதில்")
        st.markdown(result["final_answer"])
        st.write("**நிலை:**",result["status"])
        with st.expander("Verification report"):
            st.write(result["verification"])
            st.write("**Draft:**")
            st.write(result["draft"])
        st.caption("இது heuristic மற்றும் LLM self-check; formal proof அல்லது முழுமையான fact-check அல்ல.")
