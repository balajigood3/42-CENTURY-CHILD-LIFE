"""Meeting transcript analysis using deterministic local heuristics."""
from __future__ import annotations
import re
from collections import Counter

ACTION_RE = re.compile(
    r"(?P<owner>[A-Z][A-Za-z0-9_-]{1,30})\s+(?:will|to|must|should|needs to)\s+"
    r"(?P<task>[^.!?\n]{5,180})",
    re.I
)
DECISION_MARKERS = ("we decided", "decision:", "agreed that", "approved", "the team agreed")
RISK_MARKERS = ("risk:", "blocked", "blocker", "delay", "dependency", "concern:", "at risk")
STOP_WORDS = {"the","and","for","that","this","with","from","will","would","could","should",
              "have","has","had","are","was","were","you","your","they","them","their",
              "meeting","today","about","into","then","than","also","there","what","when"}

def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) > 8]

def analyze_transcript(transcript, title="Meeting", meeting_date=""):
    if not isinstance(transcript, str) or len(transcript.strip()) < 20:
        raise ValueError("Transcript must contain at least 20 characters.")
    if len(transcript) > 150_000:
        raise ValueError("Transcript exceeds the 150,000 character demo limit.")
    sentences = _sentences(transcript)
    actions, decisions, risks = [], [], []
    seen_actions = set()
    for sentence in sentences:
        match = ACTION_RE.search(sentence)
        if match:
            owner = match.group("owner").strip()
            task = match.group("task").strip(" ,;:")
            key = (owner.lower(), task.lower())
            if key not in seen_actions:
                actions.append({"owner": owner, "task": task, "status": "OPEN"})
                seen_actions.add(key)
        lower = sentence.lower()
        if any(marker in lower for marker in DECISION_MARKERS):
            decisions.append(sentence)
        if any(marker in lower for marker in RISK_MARKERS):
            risks.append(sentence)
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", transcript.lower())
    keywords = [word for word, _ in Counter(w for w in words if w not in STOP_WORDS).most_common(8)]
    summary = sentences[:5]
    return {
        "meeting_title": title.strip() or "Meeting",
        "meeting_date": meeting_date.strip(),
        "summary": summary,
        "action_items": actions,
        "decisions": list(dict.fromkeys(decisions))[:20],
        "risks_and_blockers": list(dict.fromkeys(risks))[:20],
        "key_topics": keywords,
        "follow_up_questions": [
            "Are action-item owners and due dates confirmed?",
            "Do any decisions require formal approval?",
            "Are blockers assigned to an accountable owner?"
        ],
        "disclaimer": "Heuristic transcript analysis. Verify summaries, decisions, owners and risks against the original recording or notes."
    }

def validate_analysis(result):
    required = {"meeting_title", "meeting_date", "summary", "action_items",
                "decisions", "risks_and_blockers", "key_topics",
                "follow_up_questions", "disclaimer"}
    if not isinstance(result, dict) or not required.issubset(result):
        raise ValueError("Analysis output is missing required fields.")
    if not all(isinstance(result[k], str) for k in ("meeting_title", "meeting_date", "disclaimer")):
        raise ValueError("Meeting metadata fields must be strings.")
    for key in ("summary", "decisions", "risks_and_blockers", "key_topics", "follow_up_questions", "action_items"):
        if not isinstance(result[key], list):
            raise ValueError(f"{key} must be a list.")
    for item in result["action_items"]:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(k), str) and item[k].strip() for k in ("owner", "task", "status")
        ):
            raise ValueError("Each action item requires owner, task and status.")
    return result
