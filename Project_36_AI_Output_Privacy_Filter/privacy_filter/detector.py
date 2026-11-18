"""Local pattern-based sensitive-data detection and redaction."""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern
    replacement: str

RULES = [
    Rule("email", re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"), "[REDACTED_EMAIL]"),
    Rule("phone", re.compile(r"(?<!\w)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}(?!\w)"), "[REDACTED_PHONE]"),
    Rule("credit_card", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), "[REDACTED_CARD]"),
    Rule("ipv4", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"), "[REDACTED_IP]"),
    Rule("api_key", re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b"), "[REDACTED_SECRET]"),
    Rule("india_pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[REDACTED_PAN]"),
    Rule("india_aadhaar", re.compile(r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"), "[REDACTED_ID]"),
]

def detect(text: str) -> list[dict]:
    findings = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            findings.append({
                "type": rule.name,
                "start": match.start(),
                "end": match.end(),
                "matched_text": _mask(match.group(), rule.name),
            })
    return sorted(findings, key=lambda item: (item["start"], item["end"]))

def _mask(value: str, kind: str) -> str:
    if kind == "email":
        local, _, domain = value.partition("@")
        return (local[:1] + "***@" + domain) if local else "***@" + domain
    if kind in {"credit_card", "india_aadhaar"}:
        digits = re.sub(r"\D", "", value)
        return "*" * max(0, len(digits)-4) + digits[-4:]
    if kind == "phone":
        digits = re.sub(r"\D", "", value)
        return "*" * max(0, len(digits)-4) + digits[-4:]
    return "[MASKED]"

def redact(text: str) -> tuple[str, list[dict]]:
    result = text
    # Apply from right to left so original offsets remain valid.
    findings = detect(text)
    for item in reversed(findings):
        replacement = next(rule.replacement for rule in RULES if rule.name == item["type"])
        result = result[:item["start"]] + replacement + result[item["end"]:]
    return result, findings

def filter_output(text: str, mode: str = "redact") -> dict:
    if not isinstance(text, str):
        raise TypeError("Output must be a string.")
    if mode not in {"redact", "block", "report"}:
        raise ValueError("mode must be redact, block, or report.")
    findings = detect(text)
    if mode == "redact":
        safe_text, _ = redact(text)
        status = "redacted" if findings else "clean"
    elif mode == "block":
        safe_text = "" if findings else text
        status = "blocked" if findings else "clean"
    else:
        safe_text = text
        status = "review_required" if findings else "clean"
    return {
        "status": status,
        "mode": mode,
        "finding_count": len(findings),
        "findings": findings,
        "safe_output": safe_text,
        "disclaimer": "Pattern-based screening can miss sensitive data or flag ordinary text. Review high-risk outputs before disclosure."
    }
