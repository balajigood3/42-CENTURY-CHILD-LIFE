import pytest
from knowledge_tutor.tutor import build_prompt, validate_tutor_output, fallback_tutor_output, to_markdown
from knowledge_tutor.history import save_session, load_sessions

def sample():
    return {
        "topic": "Neural Networks",
        "direct_answer": "A neural network learns patterns using connected computational units.",
        "lesson": "A network contains layers of units with weighted connections.",
        "key_concepts": [
            {"term": "Neuron", "meaning": "A computational unit."},
            {"term": "Weight", "meaning": "A learned connection parameter."}
        ],
        "worked_example": "Input values pass through weighted connections and an activation function.",
        "practice_questions": [
            {"question": f"Question {i}?", "answer": "A concise answer.",
             "explanation": "This checks understanding."} for i in range(3)
        ],
        "further_study": ["Activation functions"],
        "caveats": ["Simplified explanation."]
    }

def test_prompt_includes_question_and_level():
    prompt = build_prompt("Neural Networks", "Beginner", "What is a neuron?")
    assert "What is a neuron?" in prompt and "Beginner" in prompt

def test_missing_topic_rejected():
    with pytest.raises(ValueError):
        build_prompt(" ", "Beginner", "Explain weights")

def test_invalid_level_rejected():
    with pytest.raises(ValueError):
        build_prompt("Topic", "Expert+", "Question")

def test_valid_tutor_output_passes():
    assert validate_tutor_output(sample())["topic"] == "Neural Networks"

def test_wrong_practice_question_count_rejected():
    data = sample()
    data["practice_questions"].pop()
    with pytest.raises(ValueError):
        validate_tutor_output(data)

def test_key_concept_missing_meaning_rejected():
    data = sample()
    data["key_concepts"][0]["meaning"] = ""
    with pytest.raises(ValueError):
        validate_tutor_output(data)

def test_empty_caveat_list_allowed():
    data = sample()
    data["caveats"] = []
    assert validate_tutor_output(data)["caveats"] == []

def test_fallback_output_validates():
    data = fallback_tutor_output("Fractions", "How do fractions work?")
    assert validate_tutor_output(data)["topic"] == "Fractions"
    assert "Offline mode" in data["caveats"][0]

def test_markdown_export():
    md = to_markdown(sample())
    assert "Direct answer" in md and "Practice" in md

def test_history_round_trip(tmp_path):
    path = tmp_path / "history.jsonl"
    save_session(path, "Neural Networks", "What is a neuron?", sample())
    assert load_sessions(path)[0]["output"]["topic"] == "Neural Networks"

def test_history_limit(tmp_path):
    path = tmp_path / "history.jsonl"
    for i in range(3):
        save_session(path, str(i), "Question", sample())
    assert len(load_sessions(path, 2)) == 2
