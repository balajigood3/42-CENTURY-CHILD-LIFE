"""Turn transcribed Tamil speech into searchable knowledge notes."""
from __future__ import annotations
import re
from collections import Counter

def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?。])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]

def keywords(text: str, limit: int = 10) -> list[str]:
    tokens = re.findall(r"[\u0B80-\u0BFF]+|[A-Za-z0-9_]+", text.lower())
    stop = {"என்று", "மற்றும்", "ஒரு", "இந்த", "அது", "the", "and", "with"}
    counts = Counter(token for token in tokens if len(token) > 1 and token not in stop)
    return [word for word, _ in counts.most_common(limit)]

def create_knowledge_note(transcript: str, source_name: str = "audio") -> dict:
    if not transcript.strip():
        raise ValueError("Transcript is empty.")
    sentences = split_sentences(transcript)
    return {
        "source": source_name,
        "transcript": transcript.strip(),
        "sentence_count": len(sentences),
        "keywords": keywords(transcript),
        "key_points": sentences[:8],
        "language": "Tamil" if any("\u0B80" <= c <= "\u0BFF" for c in transcript) else "Unknown/other",
    }

def search_note(note: dict, query: str, limit: int = 4) -> list[dict]:
    terms = set(re.findall(r"[\u0B80-\u0BFF]+|[A-Za-z0-9_]+", query.lower()))
    if not terms:
        return []
    sentences = split_sentences(note.get("transcript", ""))
    matches = []
    for index, sentence in enumerate(sentences):
        sentence_terms = set(re.findall(r"[\u0B80-\u0BFF]+|[A-Za-z0-9_]+", sentence.lower()))
        score = len(terms & sentence_terms)
        if score:
            matches.append({"sentence_index": index, "score": score, "text": sentence})
    return sorted(matches, key=lambda item: (-item["score"], item["sentence_index"]))[:limit]
