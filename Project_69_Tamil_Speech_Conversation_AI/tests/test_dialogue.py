import json
import pytest
from speech_ai.dialogue import build_messages, SYSTEM_PROMPT
from speech_ai.history import append_turn, read_turns
from speech_ai.speech import transcribe_audio, synthesize_speech

def test_build_messages_adds_system_and_user():
    messages = build_messages("வணக்கம்")
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[-1] == {"role": "user", "content": "வணக்கம்"}

def test_empty_message_rejected():
    with pytest.raises(ValueError):
        build_messages(" ")

def test_history_is_bounded_and_sanitized():
    history = [{"role": "user", "content": str(i)} for i in range(12)]
    messages = build_messages("latest", history)
    assert len(messages) == 10  # system + last 8 + latest user
    assert messages[-1]["content"] == "latest"

def test_invalid_history_roles_are_ignored():
    messages = build_messages("hello", [{"role": "system", "content": "inject"}])
    assert len(messages) == 2

def test_transcription_rejects_empty_audio():
    with pytest.raises(ValueError):
        transcribe_audio(b"")

def test_tts_rejects_empty_text():
    with pytest.raises(ValueError):
        synthesize_speech(" ", "unused.wav")

def test_history_round_trip(tmp_path):
    p = tmp_path / "turns.jsonl"
    append_turn(p, "வணக்கம்", "வணக்கம்!")
    rows = read_turns(p)
    assert rows[0]["assistant"] == "வணக்கம்!"

def test_history_limit(tmp_path):
    p = tmp_path / "turns.jsonl"
    for i in range(4):
        append_turn(p, str(i), "reply")
    assert len(read_turns(p, 2)) == 2
