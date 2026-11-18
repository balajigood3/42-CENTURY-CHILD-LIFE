from src.reflection import SelfReflectionEngine

def test_round_count_is_bounded():
    # Verify bounds without making a network call by replacing generation.
    engine=SelfReflectionEngine()
    calls=[]
    def fake(prompt,temperature=0.2):
        calls.append(prompt)
        if "INITIAL ANSWER" in prompt: return "draft"
        if "CRITIQUE:" in prompt and "REVISED ANSWER" not in prompt: return "critique"
        return "revision"
    engine._generate=fake
    result=engine.run("test task",rounds=99)
    assert len(result["reflections"])==3
    assert result["final_answer"]=="revision"
    assert len(calls)==7

def test_one_round():
    engine=SelfReflectionEngine()
    engine._generate=lambda prompt,temperature=0.2: "generated"
    result=engine.run("task",rounds=1)
    assert len(result["reflections"])==1
