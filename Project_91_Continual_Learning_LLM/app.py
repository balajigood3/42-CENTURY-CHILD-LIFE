import json
import streamlit as st
from continual_learning.memory import ContinualTextLearner

st.set_page_config(page_title="Continual Learning LLM Lab", layout="wide")
st.title("Continual Learning LLM – Incremental Learning Lab")
st.caption("புதிய labeled examples-ஐ படிப்படியாக கற்றுக்கொண்டு, replay memory மூலம் பழைய வகைகளைத் தக்கவைக்கும் local experiment.")

if "learner" not in st.session_state:
    st.session_state.learner = ContinualTextLearner(replay_capacity=200)
learner = st.session_state.learner

st.info("This is a transparent online text-classification baseline, not a foundation LLM. No paid API keys or external services are used.")
tab1, tab2, tab3 = st.tabs(["Learn", "Predict & Evaluate", "Memory"])
with tab1:
    st.subheader("Add training examples")
    with st.form("learn_form"):
        text = st.text_area("Training text", "The server API request failed with a timeout.")
        label = st.text_input("Class label", "technical")
        submitted = st.form_submit_button("Learn example")
    if submitted:
        try:
            info = learner.learn(text, label)
            st.success(f"Learned. Replay memory: {info['memory_size']} examples.")
        except ValueError as exc:
            st.error(str(exc))
    uploaded = st.file_uploader("Optional JSONL training file", type=["jsonl"])
    if uploaded and st.button("Import JSONL"):
        import json
        try:
            rows = [json.loads(line) for line in uploaded.getvalue().decode("utf-8").splitlines() if line.strip()]
            result = learner.learn_batch(rows)
            st.success(f"Imported {len(result)} records.")
        except Exception as exc:
            st.error(f"Import failed: {exc}")

with tab2:
    query = st.text_area("Text to classify", "The payment invoice is overdue.")
    if st.button("Predict"):
        if learner.examples:
            st.json(learner.predict(query))
        else:
            st.warning("Train at least one example first.")
    st.markdown("**Evaluate using JSONL** (`{\"text\":\"...\", \"label\":\"...\"}` per line)")
    eval_file = st.file_uploader("Evaluation JSONL", type=["jsonl"], key="eval")
    if eval_file and st.button("Run evaluation"):
        try:
            rows = [json.loads(line) for line in eval_file.getvalue().decode("utf-8").splitlines() if line.strip()]
            st.json(learner.evaluate(rows))
        except Exception as exc:
            st.error(f"Evaluation failed: {exc}")

with tab3:
    st.metric("Replay memory examples", len(learner.examples))
    st.metric("Learned classes", len(learner.centroids))
    st.write("Vocabulary size:", len(learner.vocabulary))
    st.json(learner.to_dict())
    st.download_button("Export model memory", json.dumps(learner.to_dict(), ensure_ascii=False, indent=2),
                       file_name="continual_learning_memory.json", mime="application/json")
    saved = st.file_uploader("Restore exported model memory", type=["json"], key="restore")
    if saved and st.button("Restore memory"):
        try:
            st.session_state.learner = ContinualTextLearner.from_dict(json.loads(saved.getvalue()))
            st.success("Memory restored. Refresh the page to use the restored learner.")
        except Exception as exc:
            st.error(f"Restore failed: {exc}")
