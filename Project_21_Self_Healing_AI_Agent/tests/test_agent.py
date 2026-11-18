from app.agent import SelfHealingAgent

def test_fallback_calculator(tmp_path):
    agent = SelfHealingAgent(workspace=tmp_path, use_llm=False)
    result = agent.run("calculate 12 * 4")
    assert result["success"] is True
    assert result["results"] == ["48"]

def test_unsupported_task_returns_failure(tmp_path):
    agent = SelfHealingAgent(workspace=tmp_path, use_llm=False)
    result = agent.run("do something arbitrary")
    assert result["success"] is False
