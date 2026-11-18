import pytest
from edu_ai.generator import build_prompt, sample_content, generate_content, SUBJECTS, LEVELS, FORMATS
from edu_ai.history import save_content, load_history

def test_catalogs_are_available():
    assert "அறிவியல்" in SUBJECTS
    assert "தொடக்கநிலை" in LEVELS
    assert "வினாடி வினா" in FORMATS

def test_prompt_includes_learning_details():
    p = build_prompt("ஒளிச்சேர்க்கை", "அறிவியல்", "தொடக்கநிலை", "பாடக்குறிப்பு", "தாவர உணவு தயாரித்தல்")
    assert "ஒளிச்சேர்க்கை" in p
    assert "தாவர உணவு தயாரித்தல்" in p
    assert "தமிழில்" in p

def test_empty_topic_rejected():
    with pytest.raises(ValueError):
        build_prompt(" ", "அறிவியல்", "தொடக்கநிலை", "பாடக்குறிப்பு")

def test_invalid_subject_rejected():
    with pytest.raises(ValueError):
        sample_content("விகிதம்", "unknown", "தொடக்கநிலை", "பாடக்குறிப்பு")

def test_quiz_format_contains_answer():
    result = sample_content("எண்கள்", "கணிதம்", "தொடக்கநிலை", "வினாடி வினா")
    assert "சரியான விடை" in result

def test_worksheet_format_has_questions():
    result = sample_content("நீர்", "அறிவியல்", "நடுத்தரநிலை", "பயிற்சித்தாள்")
    assert "பற்றி இரண்டு வரிகளில்" in result

def test_generate_sample_mode():
    assert "முக்கிய கருத்துகள்" in generate_content("வாக்கியம்", "தமிழ்", "தொடக்கநிலை", "பாடக்குறிப்பு")

def test_invalid_mode_rejected():
    with pytest.raises(ValueError):
        generate_content("வாக்கியம்", "தமிழ்", "தொடக்கநிலை", "பாடக்குறிப்பு", mode="remote")

def test_history_round_trip(tmp_path):
    p = tmp_path / "history.jsonl"
    save_content(p, "நீர்", "அறிவியல்", "தொடக்கநிலை", "பாடக்குறிப்பு", "உள்ளடக்கம்", "sample")
    assert load_history(p)[0]["topic"] == "நீர்"

def test_history_limit(tmp_path):
    p = tmp_path / "history.jsonl"
    for i in range(3):
        save_content(p, str(i), "தமிழ்", "தொடக்கநிலை", "பாடக்குறிப்பு", "x", "sample")
    assert len(load_history(p, 2)) == 2
