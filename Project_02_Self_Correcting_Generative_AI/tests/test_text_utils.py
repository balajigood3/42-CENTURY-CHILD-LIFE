from utils.text_utils import clean_text, validate_question

def test_clean_text():
    assert clean_text("  Hello    Generative AI  ") == "Hello Generative AI"

def test_valid_question():
    assert validate_question("Explain Generative AI")

def test_empty_question():
    assert not validate_question("")
