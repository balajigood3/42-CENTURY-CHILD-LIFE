import pytest
from tamil_assistant.core import offline_answer
from tamil_assistant.history import append_history, read_history

def test_greeting_tamil():
    assert "வணக்கம்" in offline_answer("வணக்கம்")

def test_ai_definition():
    assert "செயற்கை நுண்ணறிவு" in offline_answer("செயற்கை நுண்ணறிவு என்றால் என்ன?")

def test_unknown_question_has_limit_notice():
    assert "offline demo" in offline_answer("இந்த உலகில் நாளை என்ன நடக்கும்?")

def test_empty_question():
    assert "கேள்வியை" in offline_answer("  ")

def test_history_round_trip(tmp_path):
    path = tmp_path / "data" / "history.jsonl"
    append_history(path, "வணக்கம்", "வணக்கம்!")
    rows = read_history(path)
    assert len(rows) == 1
    assert rows[0]["question"] == "வணக்கம்"

def test_history_ignores_malformed_lines(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text('{"question":"ok"}' + chr(10) + 'not-json' + chr(10), encoding="utf-8")
    assert len(read_history(path)) == 1
