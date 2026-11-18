"""Small continual-learning experiment using replay memory and online prototypes."""
from __future__ import annotations
import json
import math
from pathlib import Path

def tokenize(text):
    if not isinstance(text, str) or not text.strip():
        return []
    return [t.lower() for t in __import__("re").findall(r"[a-zA-Z0-9_]+", text)]

def vectorize(text, vocabulary):
    tokens = tokenize(text)
    counts = {term: 0.0 for term in vocabulary}
    for token in tokens:
        if token in counts:
            counts[token] += 1.0
    norm = math.sqrt(sum(v * v for v in counts.values()))
    return {k: (v / norm if norm else 0.0) for k, v in counts.items()}

def cosine(a, b):
    keys = set(a) | set(b)
    return sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)

class ContinualTextLearner:
    """Incremental text classifier; learns class centroids and retains replay examples."""
    def __init__(self, replay_capacity=200):
        if not isinstance(replay_capacity, int) or replay_capacity < 1:
            raise ValueError("replay_capacity must be a positive integer.")
        self.replay_capacity = replay_capacity
        self.examples = []
        self.vocabulary = set()
        self.centroids = {}

    def learn(self, text, label):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Training text must not be empty.")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must not be empty.")
        item = {"text": text.strip(), "label": label.strip()}
        self.examples.append(item)
        self.examples = self.examples[-self.replay_capacity:]
        self._rebuild()
        return {"learned": True, "label": item["label"], "memory_size": len(self.examples)}

    def learn_batch(self, records):
        if not isinstance(records, list) or not records:
            raise ValueError("Provide a non-empty list of training records.")
        return [self.learn(x.get("text"), x.get("label")) for x in records if isinstance(x, dict)]

    def _rebuild(self):
        self.vocabulary = {token for x in self.examples for token in tokenize(x["text"])}
        sums, counts = {}, {}
        for item in self.examples:
            label = item["label"]
            vec = vectorize(item["text"], self.vocabulary)
            sums.setdefault(label, {t: 0.0 for t in self.vocabulary})
            counts[label] = counts.get(label, 0) + 1
            for term, value in vec.items():
                sums[label][term] += value
        self.centroids = {
            label: {term: value / counts[label] for term, value in values.items()}
            for label, values in sums.items()
        }

    def predict(self, text):
        if not self.centroids:
            raise ValueError("The model has no training examples.")
        vec = vectorize(text, self.vocabulary)
        scores = {label: round(cosine(vec, centroid), 6)
                  for label, centroid in self.centroids.items()}
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        return {
            "label": ranked[0][0],
            "confidence_proxy": ranked[0][1],
            "scores": scores,
            "note": "Similarity score, not a calibrated probability."
        }

    def evaluate(self, records):
        if not isinstance(records, list) or not records:
            raise ValueError("Provide evaluation records.")
        correct = 0
        details = []
        for item in records:
            prediction = self.predict(item["text"])
            match = prediction["label"] == item["label"]
            correct += int(match)
            details.append({"text": item["text"], "expected": item["label"],
                            "predicted": prediction["label"], "correct": match})
        return {"accuracy": correct / len(records), "total": len(records), "details": details}

    def to_dict(self):
        return {"replay_capacity": self.replay_capacity, "examples": self.examples}

    @classmethod
    def from_dict(cls, data):
        learner = cls(data["replay_capacity"])
        for item in data["examples"]:
            learner.learn(item["text"], item["label"])
        return learner

    def save(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)
