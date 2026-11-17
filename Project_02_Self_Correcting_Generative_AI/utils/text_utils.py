def clean_text(text: str) -> str:
    return " ".join(text.strip().split())

def validate_question(question) -> bool:
    return isinstance(question, str) and bool(question.strip())
