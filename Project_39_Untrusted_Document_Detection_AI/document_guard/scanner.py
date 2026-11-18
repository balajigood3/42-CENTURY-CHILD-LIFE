"""Heuristic scanner for untrusted or instruction-like document content."""
from __future__ import annotations
import re
from pathlib import Path

RULES = {
    "instruction_override": re.compile(r"(?i)\b(ignore|disregard|override)\b.{0,80}\b(previous|prior|system|developer|instructions|rules)\b"),
    "system_prompt_extraction": re.compile(r"(?i)\b(reveal|print|show|dump|expose)\b.{0,60}\b(system prompt|hidden instructions|developer message)\b"),
    "tool_execution": re.compile(r"(?i)\b(run|execute|invoke|call)\b.{0,60}\b(shell|terminal|command|tool|function)\b"),
    "data_exfiltration": re.compile(r"(?i)\b(send|upload|forward|email|exfiltrate)\b.{0,80}\b(all|private|confidential|customer|secret|records|data)\b"),
    "credential_request": re.compile(r"(?i)\b(api[_ -]?key|password|secret token|access token)\b"),
    "authority_spoofing": re.compile(r"(?i)\b(system message|system override|administrator notice|highest priority instruction)\b"),
    "external_url": re.compile(r"https?://[^\s)\]}>\"']+", re.I),
}
INJECTION_CONTEXT = re.compile(r"(?i)(ignore.{0,30}instructions|system override|reveal.{0,30}system prompt|exfiltrate|send all records)")

def scan_text(text: str, source: str = "pasted_text") -> dict:
    if not isinstance(text, str):
        raise TypeError("Document content must be text.")
    findings = []
    for category, pattern in RULES.items():
        for match in pattern.finditer(text):
            snippet = text[max(0, match.start()-45):min(len(text), match.end()+45)].replace("\n", " ")
            findings.append({
                "category": category,
                "start": match.start(),
                "end": match.end(),
                "evidence": snippet[:180],
                "severity": "high" if category in {"instruction_override", "system_prompt_extraction", "data_exfiltration", "tool_execution"} else "medium",
            })
    findings.sort(key=lambda x: x["start"])
    high = sum(x["severity"] == "high" for x in findings)
    score = min(100, high * 20 + (len(findings)-high) * 8)
    return {
        "source": source,
        "risk_score": score,
        "risk_level": "high" if score >= 50 else "medium" if score >= 20 else "low",
        "finding_count": len(findings),
        "findings": findings,
        "recommended_action": "quarantine_and_review" if score >= 50 else "review_before_retrieval" if findings else "no_pattern_detected",
        "disclaimer": "Heuristic screening only. Absence of findings does not establish that a document is safe."
    }

def scan_file(path: str) -> dict:
    """Read only bounded text files; never execute, follow links, or parse macros."""
    file_path = Path(path)
    if file_path.suffix.lower() not in {".txt", ".md", ".csv", ".json", ".yaml", ".yml", ".xml", ".html"}:
        raise ValueError("Unsupported file type. Upload a plain-text document format.")
    if not file_path.is_file() or file_path.stat().st_size > 2_000_000:
        raise ValueError("File is missing or exceeds the 2 MB limit.")
    content = file_path.read_text(encoding="utf-8", errors="replace")
    return scan_text(content, file_path.name)
