import pytest
from indic_translate.engine import LANGUAGES, validate_language, offline_translate, translate
from indic_translate.text_utils import split_text, estimate_word_count
from indic_translate.history import save_translation, load_history

def test_language_catalog_contains_indic_languages():
    assert LANGUAGES["Tamil"] == "ta"
    assert LANGUAGES["Hindi"] == "hi"
    assert LANGUAGES["Telugu"] == "te"

def test_language_validation():
    assert validate_language("Kannada") == "kn"
    with pytest.raises(ValueError):
        validate_language("Klingon")

def test_offline_fallback_is_honest():
    result = offline_translate("Hello", "English", "Tamil")
    assert "Offline demo mode" in result
    assert "Hello" in result

def test_same_language_returns_original():
    assert translate("வணக்கம்", "Tamil", "Tamil") == "வணக்கம்"

def test_empty_text_rejected():
    with pytest.raises(ValueError):
        translate(" ", "English", "Tamil")

def test_text_chunking():
    chunks = split_text("alpha beta gamma delta epsilon", max_chars=10)
    assert len(chunks) > 1
    assert all(len(c) <= 10 for c in chunks)

def test_history_round_trip(tmp_path):
    p = tmp_path / "history.jsonl"
    save_translation(p, "Hello", "வணக்கம்", "English", "Tamil")
    rows = load_history(p)
    assert rows[0]["translated_text"] == "வணக்கம்"
