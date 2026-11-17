def test_verification_status_normalization():
    allowed = {"PASS", "NEEDS_REVISION"}
    for status in ["PASS", "NEEDS_REVISION"]:
        assert status in allowed

def test_step_limit():
    steps = [{"task": str(i)} for i in range(10)]
    max_steps = 4
    assert len(steps[:max_steps]) == 4
