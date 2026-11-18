from __future__ import annotations
import re
from dataclasses import dataclass, asdict

RULES = [
    ("policy_override", "Policy override attempt", 30, [
        r"\bignore\s+(all\s+)?(previous|prior|above)\s+(safety\s+)?(rules|instructions|polic(y|ies))\b",
        r"\bdisregard\s+(your\s+)?(safety|content|security)\s+(rules|policy|guidelines)\b",
        r"\bdisable\s+(your\s+)?(safety|content)\s+filters?\b",
        r"\bbypass\s+(your\s+)?(safety|security)\s+(rules|filters?)\b",
    ]),
    ("persona_switch", "Unsafe persona or role switch", 25, [
        r"\byou\s+are\s+now\s+(an?\s+)?(dan|evil|unfiltered|unrestricted)\b",
        r"\bact\s+as\s+(an?\s+)?(unrestricted|uncensored|unfiltered)\s+(ai|assistant|model)\b",
        r"\bpretend\s+you\s+have\s+no\s+(rules|restrictions|limitations)\b",
    ]),
    ("refusal_suppression", "Refusal suppression", 20, [
        r"\bdo\s+not\s+refuse\b",
        r"\bnever\s+say\s+you\s+cannot\b",
        r"\byou\s+must\s+answer\s+without\s+warnings\b",
    ]),
    ("encoding_obfuscation", "Encoded or obfuscated instruction cue", 20, [
        r"\bdecode\s+and\s+follow\s+the\s+instructions?\b",
        r"\bbase64\b.{0,80}\b(execute|follow|obey)\b",
        r"\brot13\b.{0,80}\b(execute|follow|obey)\b",
    ]),
    ("fictional_framing", "Fictional framing used to evade safeguards", 15, [
        r"\bfor\s+a\s+fictional\s+story\b.{0,100}\b(no\s+rules|uncensored|bypass)\b",
        r"\bin\s+a\s+hypothetical\s+world\b.{0,100}\b(ignore|bypass)\b",
    ]),
    ("multi_step_manipulation", "Multi-step manipulation cue", 25, [
        r"\bfirst\s+confirm\s+you\s+will\s+ignore\b",
        r"\bwhen\s+i\s+say\s+.*\bthen\s+reveal\b",
        r"\bthis\s+is\s+a\s+test\s+of\s+obedience\b",
    ]),
]

@dataclass
class Finding:
    category: str
    label: str
    matched_text: str
    points: int

@dataclass
class JailbreakReport:
    score: int
    severity: str
    decision: str
    findings: list[dict]
    explanation: str

def detect_jailbreak(prompt: str) -> JailbreakReport:
    findings = []
    for category, label, points, patterns in RULES:
        for pattern in patterns:
            match = re.search(pattern, prompt, flags=re.IGNORECASE | re.DOTALL)
            if match:
                findings.append(Finding(category, label, match.group(0)[:140], points))
                break
    score = min(100, sum(item.points for item in findings))
    if score >= 60:
        severity, decision = "High", "BLOCK_AND_ESCALATE"
    elif score >= 30:
        severity, decision = "Medium", "REVIEW_AND_LIMIT_PRIVILEGES"
    elif score > 0:
        severity, decision = "Low", "CAUTION_AND_MONITOR"
    else:
        severity, decision = "No configured signal", "NO_MATCH_CONTINUE_STANDARD_CHECKS"
    if findings:
        explanation = "One or more configured jailbreak-like patterns matched. Review the full context before taking action."
    else:
        explanation = "No configured jailbreak pattern matched. This does not prove the prompt is safe."
    return JailbreakReport(score, severity, decision, [asdict(f) for f in findings], explanation)
