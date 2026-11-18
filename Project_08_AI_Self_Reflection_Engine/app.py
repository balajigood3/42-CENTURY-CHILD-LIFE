import streamlit as st
from src.reflection import SelfReflectionEngine

st.set_page_config(page_title="AI Self-Reflection Engine",layout="wide")
st.title("AI Self-Reflection Engine")
st.caption("ஒரு ஆரம்ப பதிலை உருவாக்கி, அதை விமர்சித்து, திருத்தப்பட்ட பதிலை வழங்கும் Local GenAI பயன்பாடு.")
with st.sidebar:
    model=st.text_input("Ollama model","qwen2.5:3b")
    url=st.text_input("Ollama URL","http://localhost:11434")
    rounds=st.slider("Reflection rounds",1,3,2)
    st.caption("Paid API key தேவையில்லை. `ollama pull qwen2.5:3b` இயக்கவும்.")
engine=SelfReflectionEngine(model,url)
question=st.text_area("கேள்வி / பணி",height=150,placeholder="உதா: RAG architecture-ஐ விளக்கவும்.")
if st.button("Reflect and improve",type="primary"):
    if not question.strip(): st.warning("கேள்வியை உள்ளிடவும்.")
    else:
        with st.spinner("Draft → critique → revision..."):
            result=engine.run(question,rounds)
        st.subheader("Final answer")
        st.markdown(result["final_answer"])
        for i,step in enumerate(result["reflections"],1):
            with st.expander(f"Reflection round {i}"):
                st.markdown("**Critique**")
                st.write(step["critique"])
                st.markdown("**Revised draft**")
                st.write(step["revision"])
        st.info("Self-reflection என்பது model உருவாக்கும் மதிப்பீடு மட்டுமே; வெளிப்புற உண்மைச் சரிபார்ப்பு அல்ல.")
