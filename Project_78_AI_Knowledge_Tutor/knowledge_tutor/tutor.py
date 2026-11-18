"""Knowledge tutoring workflow with validated lessons and quizzes."""
import re

LEVELS = {"School", "Beginner", "Intermediate", "Advanced"}
LESSON_LENGTHS = {"Short", "Detailed", "Exam-focused"}

def build_prompt(topic, learner_level, question, reference_notes="", lesson_length="Detailed"):
    if not topic.strip() or not question.strip():
        raise ValueError("Topic and learner question are required.")
    if learner_level not in LEVELS:
        raise ValueError("Unsupported learner level.")
    if lesson_length not in LESSON_LENGTHS:
        raise ValueError("Unsupported lesson format.")
    return f"""
You are a patient, accurate knowledge tutor.
Topic: {topic.strip()}
Learner level: {learner_level}
Learner question: {question.strip()}
Reference notes supplied by learner: {reference_notes.strip()}
Lesson format: {lesson_length}

Return valid JSON only:
{{
  "topic": "topic",
  "direct_answer": "answer the learner's question directly",
  "lesson": "structured level-appropriate explanation",
  "key_concepts": [{{"term": "term", "meaning": "meaning"}}],
  "worked_example": "a step-by-step example",
  "practice_questions": [
    {{"question": "question", "answer": "answer", "explanation": "why"}}
  ],
  "further_study": ["next concept to learn"],
  "caveats": ["uncertainty or limitations"]
}}
Rules:
- Include exactly 3 practice_questions.
- Use reference notes as context, but flag conflicts or uncertainty instead of blindly accepting them.
- Explain jargon at the selected level.
- Do not invent citations, URLs, or guaranteed facts.
- Keep the direct answer focused on the question.
""".strip()

def validate_tutor_output(data):
    if not isinstance(data, dict):
        raise ValueError("Tutor output must be a JSON object.")
    for field in ("topic", "direct_answer", "lesson", "worked_example"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"Missing or invalid field: {field}")
    concepts = data.get("key_concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValueError("key_concepts must be a non-empty list.")
    for i, item in enumerate(concepts, 1):
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item[k].strip() for k in ("term", "meaning")
        ):
            raise ValueError(f"Key concept {i} must include term and meaning.")
    questions = data.get("practice_questions")
    if not isinstance(questions, list) or len(questions) != 3:
        raise ValueError("Exactly 3 practice questions are required.")
    for i, item in enumerate(questions, 1):
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item[k].strip()
            for k in ("question", "answer", "explanation")
        ):
            raise ValueError(f"Practice question {i} is incomplete.")
    for field in ("further_study", "caveats"):
        if not isinstance(data.get(field), list) or not all(
            isinstance(x, str) and x.strip() for x in data[field]
        ):
            raise ValueError(f"{field} must be a list of non-empty strings.")
    return data

def fallback_tutor_output(topic, question, reference_notes=""):
    if not topic.strip() or not question.strip():
        raise ValueError("Topic and learner question are required.")
    note = reference_notes.strip() or "No reference notes were supplied."
    return {
        "topic": topic.strip(),
        "direct_answer": f"இந்தக் கேள்விக்கான பதிலை {topic.strip()} பற்றிய அடிப்படை வரையறை மற்றும் எடுத்துக்காட்டுகளுடன் ஆராய வேண்டும். Offline mode தனிப்பட்ட பதிலை உருவாக்காது.",
        "lesson": f"## கற்றல் வழிகாட்டி\n\n1. {topic.strip()}-ன் வரையறையைப் படிக்கவும்.\n2. அதன் முக்கிய கூறுகளை அடையாளம் காணவும்.\n3. ஒரு எளிய எடுத்துக்காட்டை உருவாக்கவும்.\n\n**Reference notes:** {note}",
        "key_concepts": [
            {"term": "Definition", "meaning": "கருத்தின் அடிப்படை பொருள்."},
            {"term": "Components", "meaning": "கருத்தை உருவாக்கும் முக்கிய பகுதிகள்."}
        ],
        "worked_example": f"Step 1: {topic.strip()} தொடர்பான ஒரு சிறிய உதாரணத்தைத் தேர்ந்தெடுக்கவும். Step 2: ஒவ்வொரு கூறையும் விளக்கவும். Step 3: உங்கள் விளக்கத்தை reference notes-உடன் ஒப்பிடவும்.",
        "practice_questions": [
            {"question": f"What is {topic.strip()}?", "answer": "Define it using your study material.", "explanation": "A definition checks basic understanding."},
            {"question": f"Name one key component of {topic.strip()}.", "answer": "Use a component from your notes.", "explanation": "Identifying components checks conceptual structure."},
            {"question": f"Give one application of {topic.strip()}.", "answer": "Choose a relevant real-world example.", "explanation": "Applications connect theory with practice."}
        ],
        "further_study": ["Review prerequisites", "Practice a real-world example"],
        "caveats": ["Offline mode is a generic study scaffold and does not generate a topic-specific expert answer."]
    }

def to_markdown(data):
    data = validate_tutor_output(data)
    lines = [f"# Knowledge Tutor: {data['topic']}", "", "## Direct answer",
             data["direct_answer"], "", "## Lesson", data["lesson"], "", "## Key concepts"]
    for item in data["key_concepts"]:
        lines += [f"- **{item['term']}:** {item['meaning']}"]
    lines += ["", "## Worked example", data["worked_example"], "", "## Practice"]
    for i, q in enumerate(data["practice_questions"], 1):
        lines += [f"### {i}. {q['question']}", f"**Answer:** {q['answer']}",
                  f"**Explanation:** {q['explanation']}", ""]
    lines += ["## Further study"] + [f"- {x}" for x in data["further_study"]]
    lines += ["", "## Caveats"] + [f"- {x}" for x in data["caveats"]]
    return "\n".join(lines)
