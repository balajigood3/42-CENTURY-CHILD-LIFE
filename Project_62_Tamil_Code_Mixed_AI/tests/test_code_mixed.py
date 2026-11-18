import pytest
from code_mixed.normalizer import normalize_code_mixed, detect_script_mix, extract_terms
from code_mixed.assistant import answer, offline_reply

def test_tanglish_phrase_normalization():
    assert normalize_code_mixed("RAG na enna?") == "rag என்றால் என்ன?"

def test_multiple_phrases_normalized():
    result = normalize_code_mixed("AI na enna simple ah sollu")
    assert "ai என்றால் என்ன" in result
    assert "எளிமையாகச் சொல்லுங்கள்" in result

def test_detect_mixed_script():
    assert detect_script_mix("தமிழ் AI").get("label") == "tamil_english_mixed"

def test_detect_tamil_only():
    assert detect_script_mix("வணக்கம்").get("label") == "tamil"

def test_offline_ai_answer():
    assert "செயற்கை நுண்ணறிவு" in offline_reply("AI na enna?")

def test_empty_question_rejected():
    with pytest.raises(ValueError):
        answer("   ")

def test_extract_terms():
    assert "RAG" in extract_terms("RAG என்றால் என்ன")
