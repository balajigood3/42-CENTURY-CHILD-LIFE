import re

def find_passages(text: str, query: str, limit: int = 5) -> list[dict]:
    terms = {t.lower() for t in re.findall(r"[\w'-]+", query) if len(t) > 1}
    if not terms:
        return []
    passages = re.split(r"(?<=[.!?])\s+|\n+", text)
    results = []
    for idx, passage in enumerate(passages):
        words = {w.lower() for w in re.findall(r"[\w'-]+", passage)}
        score = len(terms & words)
        if score:
            results.append({"passage_index": idx, "score": score, "text": passage.strip()})
    return sorted(results, key=lambda x: (-x["score"], x["passage_index"]))[:limit]
