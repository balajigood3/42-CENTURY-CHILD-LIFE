from __future__ import annotations
import re
from dataclasses import dataclass, asdict

PATTERNS = [
    ("email", "Personal data", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[REDACTED_EMAIL]", 20),
    ("phone", "Personal data", re.compile(r"(?<!\w)(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{5,8}(?!\w)"), "[REDACTED_PHONE]", 20),
    ("aadhaar_like", "Government identifier", re.compile(r"(?<!\d)\d{4}\s?\d{4}\s?\d{4}(?!\d)"), "[REDACTED_GOV_ID]", 40),
    ("pan_like", "Government identifier", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b", re.I), "[REDACTED_GOV_ID]", 40),
    ("credit_card_like", "Financial data", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), "[REDACTED_PAYMENT_CARD]", 50),
    ("api_key_assignment", "Credential", re.compile(r"(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key|password|token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{6,})"), "[REDACTED_SECRET]", 60),
    ("private_key_header", "Credential", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "[REDACTED_PRIVATE_KEY]", 70),
]

@dataclass
class Finding:
    category: str
    data_type: str
    matched_text: str
    risk_points: int
    replacement: str

@dataclass
class ScanReport:
    risk_score: int
    risk_level: str
    finding_count: int
    findings: list[dict]
    sanitized_text: str
    recommendation: str

def _luhn_valid(value: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", value)]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0

def scan_text(text: str) -> ScanReport:
    findings: list[Finding] = []
    sanitized = text
    score = 0
    for category, data_type, pattern, replacement, points in PATTERNS:
        matches = list(pattern.finditer(text))
        for match in matches:
            value = match.group(0)
            if category == "credit_card_like" and not _luhn_valid(value):
                continue
            # Avoid reporting overlapping matches twice.
            if any(f.matched_text == value for f in findings):
                continue
            findings.append(Finding(category, data_type, value, points, replacement))
            score = min(100, score + points)
    # Mask longer values first to avoid partial replacement collisions.
    for finding in sorted(findings, key=lambda f: len(f.matched_text), reverse=True):
        sanitized = sanitized.replace(finding.matched_text, finding.replacement)
    if score >= 60:
        level, recommendation = "High", "BLOCK_OR_REDACT_BEFORE_SHARING"
    elif score >= 25:
        level, recommendation = "Medium", "REVIEW_AND_REDACT"
    elif score > 0:
        level, recommendation = "Low", "REDACT_BEFORE_EXTERNAL_SHARING"
    else:
        level, recommendation = "None detected", "NO_CONFIGURED_PATTERN_MATCHED"
    return ScanReport(score, level, len(findings), [asdict(f) for f in findings], sanitized, recommendation)
