from src.assistant import AdaptiveAssistant

def test_prompt_uses_preferences():
    p=AdaptiveAssistant().build_prompt("Explain RAG",{"tone":"Academic","detail":"Detailed","language":"English"})
    assert "Academic" in p and "thorough explanation" in p and "Respond in English" in p

def test_prompt_has_safe_uncertainty_instruction():
    p=AdaptiveAssistant().build_prompt("Question",{})
    assert "Do not invent facts" in p
