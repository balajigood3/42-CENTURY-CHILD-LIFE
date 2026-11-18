import pytest
from audio_knowledge import validate_audio, build_knowledge, MAX_BYTES

def test_accepts_supported_audio():
    validate_audio("meeting.WAV", 1024)

@pytest.mark.parametrize("name", ["recording.txt", "audio", "track.aac"])
def test_rejects_unsupported_extension(name):
    with pytest.raises(ValueError):
        validate_audio(name, 10)

def test_rejects_empty_and_oversized_files():
    with pytest.raises(ValueError):
        validate_audio("a.wav", 0)
    with pytest.raises(ValueError):
        validate_audio("a.wav", MAX_BYTES + 1)

def test_builds_structured_knowledge():
    result = build_knowledge(
        "Project Atlas starts Monday. We need to review the dataset. "
        "Please send the report to Priya by Friday."
    )
    assert result["summary"].startswith("Project Atlas")
    assert len(result["key_points"]) == 3
    assert len(result["action_items"]) == 2
    assert "Atlas" in result["terms"]
    assert result["word_count"] > 0
    assert result["faq_candidates"]

def test_empty_transcript_rejected():
    with pytest.raises(ValueError):
        build_knowledge("   ")
