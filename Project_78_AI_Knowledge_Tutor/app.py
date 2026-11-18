import streamlit as st
from knowledge_tutor.tutor import fallback_tutor_output, to_markdown
from knowledge_tutor.llm import generate_tutor_output
from knowledge_tutor.history import save_session, load_sessions

st.set_page_config(page_title="AI Knowledge Tutor", layout="wide")
st.title("AI Knowledge Tutor")
st.caption("கேள்விகளுக்கு விளக்கம், முக்கியக் கருத்துகள், எடுத்துக்காட்டுகள் மற்றும் பயிற்சிகளுடன் கற்றுக்கொள்ளுங்கள்.")

with st.form("tutor_form"):
    topic = st.text_input("Topic", placeholder="e.g. Neural Networks")
    question = st.text_area("What do you want to understand?",
                            placeholder="e.g. How does backpropagation work?")
    level = st.selectbox("Learner level", ["School", "Beginner", "Intermediate", "Advanced"])
    lesson_length = st.selectbox("Lesson style", ["Short", "Detailed", "Exam-focused"], index=1)
    reference = st.text_area("Reference notes (optional)")
    model = st.text_input("Ollama model", "qwen2.5:3b")
    mode = st.radio("Mode", ["Local Ollama AI", "Offline study scaffold"], horizontal=True)
    submitted = st.form_submit_button("Ask tutor", type="primary")

if submitted:
    try:
        output = (generate_tutor_output(topic, level, question, reference, lesson_length, model=model)
                  if mode == "Local Ollama AI"
                  else fallback_tutor_output(topic, question, reference))
        st.session_state["tutor_output"] = output
        save_session("data/tutor_history.jsonl", topic, question, output)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))

if st.session_state.get("tutor_output"):
    output = st.session_state["tutor_output"]
    st.subheader(output["topic"])
    st.markdown("### Direct answer")
    st.write(output["direct_answer"])
    st.markdown("### Lesson")
    st.markdown(output["lesson"])
    st.markdown("### Key concepts")
    for item in output["key_concepts"]:
        st.markdown(f"- **{item['term']}:** {item['meaning']}")
    st.markdown("### Worked example")
    st.write(output["worked_example"])
    st.markdown("### Practice questions")
    for i, q in enumerate(output["practice_questions"], 1):
        with st.expander(f"{i}. {q['question']}"):
            st.write("Answer: " + q["answer"])
            st.caption(q["explanation"])
    st.markdown("### Further study")
    for item in output["further_study"]:
        st.markdown(f"- {item}")
    if output["caveats"]:
        st.warning(" ".join(output["caveats"]))
    st.download_button("Download lesson", to_markdown(output),
                       "knowledge_tutor_lesson.md", mime="text/markdown")

with st.expander("Recent learning sessions"):
    for record in reversed(load_sessions("data/tutor_history.jsonl", 10)):
        st.write(f"{record['topic']} · {record['question'][:90]} · {record['created_at'][:10]}")
