import streamlit as st
from src.analyzer import KnowledgeGapAnalyzer
from src.store import HistoryStore

st.set_page_config(page_title="AI Knowledge Gap Detector", page_icon="🔎", layout="wide")
st.title("AI Knowledge Gap Detection System")
st.write("ஒரு ஆவணம் அல்லது பதிலில் உள்ள தகவல் குறைபாடுகள், பதிலளிக்கப்படாத கேள்விகள், தேவையான ஆதாரங்கள் ஆகியவற்றைக் கண்டறியுங்கள்.")
with st.sidebar:
    st.subheader("Local model")
    model = st.text_input("Ollama model", "qwen2.5:3b")
    url = st.text_input("Ollama URL", "http://localhost:11434")
    st.caption("API key தேவையில்லை. Ollama-ஐ நிறுவி `ollama pull qwen2.5:3b` இயக்கவும்.")

analyzer = KnowledgeGapAnalyzer(model=model, base_url=url)
history = HistoryStore()
tab1, tab2 = st.tabs(["ஆய்வு", "முந்தைய ஆய்வுகள்"])
with tab1:
    context = st.text_area("ஆய்வு செய்ய வேண்டிய உரை / ஆவண உள்ளடக்கம்", height=260,
        placeholder="உதாரணம்: இந்த அமைப்பு பயனர்களின் தரவைச் சேமிக்கிறது. தரவு எவ்வாறு பாதுகாக்கப்படுகிறது என்பது குறிப்பிடப்படவில்லை.")
    goal = st.text_input("ஆய்வின் நோக்கம் (விருப்பம்)", placeholder="உதா: பாதுகாப்பு மதிப்பாய்வு / திட்ட முன்மொழிவு / பாடக்குறிப்பு")
    if st.button("Knowledge gaps கண்டறி", type="primary"):
        if not context.strip():
            st.warning("ஆய்வு செய்ய உரையை உள்ளிடவும்.")
        else:
            with st.spinner("தகவல் குறைபாடுகள் ஆய்வு செய்யப்படுகின்றன..."):
                result = analyzer.analyze(context, goal)
                history.save(context, goal, result)
            st.subheader("சுருக்கம்")
            st.write(result.get("summary", ""))
            st.metric("கண்டறியப்பட்ட குறைபாடுகள்", len(result.get("gaps", [])))
            for idx, gap in enumerate(result.get("gaps", []), 1):
                with st.expander(f"{idx}. {gap.get('topic', 'குறிப்பிடப்படாத பகுதி')} — {gap.get('priority', 'medium')}"):
                    st.write("**எது இல்லை?**", gap.get("missing_information", ""))
                    st.write("**ஏன் முக்கியம்?**", gap.get("why_it_matters", ""))
                    st.write("**கேட்க வேண்டிய கேள்வி:**", gap.get("question_to_resolve", ""))
                    st.write("**தேவையான ஆதாரம்:**", gap.get("evidence_needed", ""))
            if result.get("strengths"):
                st.subheader("ஏற்கனவே உள்ள தகவல்")
                for item in result["strengths"]:
                    st.write(f"- {item}")
            st.info("இது உரை சார்ந்த AI ஆய்வு. கண்டறியப்படாத குறைபாடுகள் இல்லை என்று உறுதி செய்யாது; முக்கிய முடிவுகளை மனிதர் சரிபார்க்க வேண்டும்.")
with tab2:
    for row in history.recent():
        with st.expander(f"#{row['id']} · {row['created_at']}"):
            st.write("**நோக்கம்:**", row["goal"] or "குறிப்பிடப்படவில்லை")
            st.write(row["input_text"])
            st.json(row["result"])
