import json
import pytest
from continual_learning.memory import ContinualTextLearner, tokenize, vectorize, cosine

def test_tokenize_lowercases():
    assert tokenize("Hello WORLD!") == ["hello", "world"]

def test_vectorize_unit_norm():
    vec = vectorize("alpha beta beta", {"alpha", "beta"})
    assert sum(v*v for v in vec.values()) == pytest.approx(1.0)

def test_cosine_identical_vectors():
    assert cosine({"x": 1.0}, {"x": 1.0}) == pytest.approx(1.0)

def test_learn_and_predict():
    model = ContinualTextLearner()
    model.learn("server timeout api error", "technical")
    model.learn("invoice payment overdue finance", "billing")
    assert model.predict("api server timeout")["label"] == "technical"

def test_empty_training_rejected():
    with pytest.raises(ValueError):
        ContinualTextLearner().learn("", "x")

def test_empty_label_rejected():
    with pytest.raises(ValueError):
        ContinualTextLearner().learn("some text", "")

def test_empty_prediction_model_rejected():
    with pytest.raises(ValueError):
        ContinualTextLearner().predict("text")

def test_replay_capacity_bounds_memory():
    model = ContinualTextLearner(replay_capacity=2)
    model.learn("first example", "a")
    model.learn("second example", "b")
    model.learn("third example", "c")
    assert len(model.examples) == 2
    assert {x["label"] for x in model.examples} == {"b", "c"}

def test_batch_learning():
    model = ContinualTextLearner()
    out = model.learn_batch([{"text": "red apple", "label": "fruit"},
                             {"text": "blue car", "label": "vehicle"}])
    assert len(out) == 2

def test_evaluation():
    model = ContinualTextLearner()
    model.learn("apple banana fruit", "fruit")
    model.learn("truck engine road", "vehicle")
    result = model.evaluate([{"text": "banana apple", "label": "fruit"},
                             {"text": "truck road", "label": "vehicle"}])
    assert result["accuracy"] == 1.0

def test_save_and_load(tmp_path):
    model = ContinualTextLearner()
    model.learn("apple fruit", "food")
    path = tmp_path / "memory.json"
    model.save(path)
    restored = ContinualTextLearner.load(path)
    assert restored.predict("apple")["label"] == "food"

def test_invalid_capacity_rejected():
    with pytest.raises(ValueError):
        ContinualTextLearner(replay_capacity=0)
