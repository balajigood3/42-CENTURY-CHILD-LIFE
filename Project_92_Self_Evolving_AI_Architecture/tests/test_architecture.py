import json
import pytest
from evolving_ai.architecture import (
    propose_architecture, evaluate_architecture, propose_evolution, save_json
)

REQ = {"goal": "Build a knowledge assistant", "needs": ["retrieval", "memory"], "budget": 10}

def test_proposal_includes_core_components():
    result = propose_architecture(REQ)
    names = {x["name"] for x in result["components"]}
    assert {"validation", "evaluation", "retrieval", "memory"} <= names

def test_blank_goal_rejected():
    with pytest.raises(ValueError):
        propose_architecture({"goal": " ", "needs": [], "budget": 5})

def test_unknown_component_rejected():
    with pytest.raises(ValueError):
        propose_architecture({"goal": "x", "needs": ["self_modify"], "budget": 10})

def test_budget_overrun_rejected():
    with pytest.raises(ValueError):
        propose_architecture({"goal": "x", "needs": ["retrieval", "planner"], "budget": 2})

def test_duplicate_needs_deduplicated():
    result = propose_architecture({"goal": "x", "needs": ["memory", "memory"], "budget": 10})
    names = [x["name"] for x in result["components"]]
    assert len(names) == len(set(names))

def test_healthy_evaluation():
    arch = propose_architecture(REQ)
    result = evaluate_architecture(arch, [{"name": "a", "passed": True},
                                          {"name": "b", "passed": True}])
    assert result["status"] == "healthy"
    assert result["pass_rate"] == 1.0

def test_unstable_evaluation():
    arch = propose_architecture(REQ)
    result = evaluate_architecture(arch, [{"name": "a", "passed": False},
                                          {"name": "b", "passed": False}])
    assert result["status"] == "unstable"

def test_invalid_test_result_rejected():
    arch = propose_architecture(REQ)
    with pytest.raises(ValueError):
        evaluate_architecture(arch, [{"name": "a", "passed": "yes"}])

def test_evolution_requires_approval_and_never_auto_applies():
    arch = propose_architecture(REQ)
    evaluation = evaluate_architecture(arch, [{"name": "a", "passed": False}])
    proposal = propose_evolution(arch, evaluation)
    assert proposal["approval_required"] is True
    assert proposal["automatic_application"] is False

def test_healthy_evolution_has_no_changes():
    arch = propose_architecture(REQ)
    evaluation = evaluate_architecture(arch, [{"name": "a", "passed": True}])
    assert propose_evolution(arch, evaluation)["proposed_components_to_add"] == []

def test_json_export(tmp_path):
    arch = propose_architecture(REQ)
    path = tmp_path / "arch.json"
    save_json(arch, path)
    assert json.loads(path.read_text())["goal"] == REQ["goal"]

def test_no_version_auto_increment():
    arch = propose_architecture(REQ)
    evaluation = evaluate_architecture(arch, [{"name": "a", "passed": True}])
    assert evaluation["next_version_created"] is False
