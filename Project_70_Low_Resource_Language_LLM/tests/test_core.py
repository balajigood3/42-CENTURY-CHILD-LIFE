import pytest
from lowres_llm.language import detect_script, LANGUAGES
from lowres_llm.prompting import build_prompt
from lowres_llm.evaluation import script_match_ratio, basic_output_checks
from lowres_llm.history import save_record, load_records

def test_detect_tamil_script():
    assert detect_script("வணக்கம்") == "Tamil"

def test_detect_devanagari_script():
    assert detect_script("नमस्ते") == "Devanagari"

def test_detect_latin_script():
    assert detect_script("Hello world") == "Latin"

def test_unknown_script_for_symbols():
    assert detect_script("123!?") == "Unknown"

def test_prompt_names_output_language_and_task():
    prompt = build_prompt("வணக்கம்", "Tamil", "உரையாடல்")
    assert "Tamil" in prompt
    assert "உரையாடல்" in prompt

def test_empty_prompt_input_rejected():
    with pytest.raises(ValueError):
        build_prompt(" ", "Tamil", "சுருக்கம்")

def test_invalid_language_rejected():
    with pytest.raises(ValueError):
        build_prompt("hello", "Klingon", "உரையாடல்")

def test_script_ratio():
    assert script_match_ratio("வணக்கம்", "Tamil") == 1.0

def test_basic_output_checks():
    checks = basic_output_checks("தமிழ் உரை")
    assert checks["non_empty"] is True
    assert checks["word_count"] == 2

def test_history_round_trip(tmp_path):
    p = tmp_path / "history.jsonl"
    save_record(p, "Tamil", "உரையாடல்", "Hi", "வணக்கம்")
    assert load_records(p)[0]["output"] == "வணக்கம்"

def test_history_limit(tmp_path):
    p = tmp_path / "history.jsonl"
    for i in range(3):
        save_record(p, "Tamil", "உரையாடல்", str(i), "பதில்")
    assert len(load_records(p, 2)) == 2
