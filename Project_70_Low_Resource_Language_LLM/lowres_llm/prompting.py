"""Prompt construction for low-resource language tasks."""
from .language import LANGUAGES

TASKS = ["உரையாடல்", "எளிய விளக்கம்", "சுருக்கம்", "மொழிபெயர்ப்பு", "கேள்வி-பதில்"]

def build_prompt(text: str, language: str, task: str, context: str = "") -> str:
    if not text.strip():
        raise ValueError("Input text cannot be empty.")
    if language not in LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")
    if task not in TASKS:
        raise ValueError(f"Unsupported task: {task}")
    lang = language
    extra = f"\nContext: {context.strip()}" if context.strip() else ""
    instructions = {
        "உரையாடல்": "Respond helpfully and naturally in the requested language.",
        "எளிய விளக்கம்": "Explain the input in simple language with one useful example.",
        "சுருக்கம்": "Summarize the input faithfully without adding unsupported facts.",
        "மொழிபெயர்ப்பு": "Translate the input into the requested language while preserving meaning.",
        "கேள்வி-பதில்": "Answer the question in the requested language. State uncertainty when needed.",
    }
    return (
        f"You are a careful multilingual assistant. The required output language is {lang}. "
        f"Use the {LANGUAGES[language]['script']} script when applicable. "
        "Preserve names, numbers, and factual meaning. If you are uncertain, say so. "
        f"Task: {task}. {instructions[task]}\nInput:\n{text.strip()}{extra}\n"
        f"Output only in {lang}, unless the task explicitly requires otherwise."
    )
