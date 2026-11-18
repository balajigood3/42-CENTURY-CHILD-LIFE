import io
import wave
import pytest
from multimodal_assistant.processors import classify_file, validate_upload, process_text, build_response, process_audio

def test_classifies_supported_modalities():
    assert classify_file("notes.txt") == "text"
    assert classify_file("scan.pdf") == "pdf"
    assert classify_file("photo.png") == "image"
    assert classify_file("voice.wav") == "audio"

def test_rejects_unknown_file():
    with pytest.raises(ValueError):
        validate_upload("program.exe", b"abc")

def test_rejects_oversized_file():
    with pytest.raises(ValueError):
        validate_upload("notes.txt", b"x" * (15 * 1024 * 1024 + 1))

def test_requires_bytes():
    with pytest.raises(TypeError):
        validate_upload("notes.txt", "not bytes")

def test_text_decode():
    assert process_text("hello".encode()) == "hello"

def test_build_response_counts_words():
    result = build_response("one two three", "text")
    assert result["word_count"] == 3
    assert result["character_count"] == 13

def test_empty_content_message():
    assert "No text" in build_response("")["preview"]

def test_wav_metadata():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(bytes(2) * 8000)
    result = process_audio(buffer.getvalue(), "sample.wav")
    assert result["duration_seconds"] == 1.0
    assert result["sample_rate"] == 8000
