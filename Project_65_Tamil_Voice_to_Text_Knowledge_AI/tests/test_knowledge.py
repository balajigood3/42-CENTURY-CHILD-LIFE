import pytest
from voice_knowledge.knowledge import split_sentences, keywords, create_knowledge_note, search_note
from voice_knowledge.storage import save_note, load_notes
from voice_knowledge.transcribe import transcribe_audio, TranscriptionError

def test_sentence_split():
    assert split_sentences("முதல் வாக்கியம். இரண்டாவது வாக்கியம்.") == ["முதல் வாக்கியம்.", "இரண்டாவது வாக்கியம்."]

def test_keyword_extraction():
    assert "தமிழ்" in keywords("தமிழ் குரல் தமிழ் உரை")

def test_note_creation():
    note = create_knowledge_note("தமிழ் குரல் பதிவு. செயற்கை நுண்ணறிவு பாடம்.", "lesson")
    assert note["sentence_count"] == 2
    assert note["language"] == "Tamil"

def test_search_note():
    note = create_knowledge_note("தமிழ் குரல் பதிவு. செயற்கை நுண்ணறிவு பாடம்.", "lesson")
    assert search_note(note, "செயற்கை நுண்ணறிவு")

def test_empty_transcript_rejected():
    with pytest.raises(ValueError):
        create_knowledge_note("  ")

def test_storage_round_trip(tmp_path):
    note = create_knowledge_note("தமிழ் உரை.", "my lesson")
    save_note(note, tmp_path)
    loaded = load_notes(tmp_path)
    assert len(loaded) == 1
    assert loaded[0]["source"] == "my lesson"

def test_missing_audio_file():
    with pytest.raises(TranscriptionError):
        transcribe_audio("/not/a/real/file.wav")
