"""Deterministic, non-executing security checks for LLM application configs."""
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any

SECRET_PATTERNS = [
    ("OpenAI-style API key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Generic credential assignment", re.compile(r"(?i)\b(api[_-]?key|password|secret|token)\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{8,})")),
]
DANGEROUS_TERMS = {
    "shell": ("shell", "exec", "subprocess", "command execution"),
    "filesystem": ("filesystem_write", "file_write", " unrestricted file"),
    "network": (" unrestricted_url", "allow_all_urls", " arbitrary_url"),
}
HIGH_IMPACT = {"delete", "transfer", "payment", "send_email", "admin", "execute"}

def parse_config(raw: str, filename: str = "config.json") -> dict[str, Any]:
    suffix = Path(filename).suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise ValueError("YAML support unavailable; install PyYAML.") from exc
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON/YAML object.")
    return data

def _walk(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from _walk(value, f"{path}[{i}]")
    else:
        yield path, str(obj)

def _redact(value: str) -> str:
    value = re.sub(r"(?i)(api[_-]?key|password|secret|token)(\s*[:=]\s*)['\"]?[^,\s'\"]+", r"\1\2[REDACTED]", value)
    for _, pattern in SECRET_PATTERNS:
        value = pattern.sub("[REDACTED_SECRET]", value)
    return value[:180]

def audit_config(config: dict[str, Any]) -> dict[str, Any]:
    """Inspect config values only. Never imports, executes, or follows referenced resources."""
    serialized = json.dumps(config, ensure_ascii=False, default=str)
    findings: list[dict[str, str]] = []

    def add(severity, category, evidence, explanation, remediation):
        findings.append({
            "severity": severity, "category": category,
            "evidence": _redact(evidence), "explanation": explanation,
            "remediation": remediation,
        })

    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(serialized):
            add("critical", "Secret exposure", match.group(0),
                f"Possible {label} embedded in configuration.",
                "Move credentials to a secret manager or environment variable; rotate exposed credentials.")

    lower = serialized.lower()
    tools = config.get("tools", [])
    if isinstance(tools, list):
        for tool in tools:
            if not isinstance(tool, dict):
                continue
            name = str(tool.get("name", "unnamed tool"))
            description = str(tool.get("description", "")).lower()
            combined = (name + " " + description).lower()
            if any(term in combined for term in ("shell", "exec", "subprocess", "run command")):
                add("critical", "Dangerous tool capability", name,
                    "A tool appears capable of running arbitrary commands.",
                    "Remove arbitrary command execution or enforce a narrow allowlist in an isolated sandbox.")
            if any(term in combined for term in HIGH_IMPACT) and not tool.get("requires_approval", False):
                add("high", "High-impact tool without approval", name,
                    "A high-impact action appears to lack explicit human approval.",
                    "Require human confirmation and enforce server-side authorization before execution.")

    checks = [
        ("document_acl", "Document access control missing", "high",
         "RAG/document retrieval has no visible document-level access control.",
         "Apply authorization filters before retrieval and re-check permissions before returning content."),
        ("output_validation", "Output validation missing", "medium",
         "No output validation setting is configured.",
         "Validate model output against a strict schema and reject or repair invalid responses."),
        ("rate_limit", "Rate limiting missing", "medium",
         "No rate-limit setting is configured.",
         "Apply per-user and per-IP quotas with abuse monitoring."),
        ("audit_logging", "Security audit logging missing", "medium",
         "No security audit logging setting is configured.",
         "Record security-relevant events while redacting secrets and sensitive user content."),
        ("url_allowlist", "URL allowlist missing", "high",
         "No outbound URL allowlist is configured.",
         "Restrict outbound requests to approved hosts and block private, loopback, and metadata IP ranges."),
        ("human_approval", "Human approval policy missing", "high",
         "No global human approval policy is configured.",
         "Require approval for external side effects and irreversible operations."),
    ]
    for key, title, severity, explanation, remediation in checks:
        if not config.get(key):
            add(severity, title, key, explanation, remediation)

    prompt = str(config.get("system_prompt", "")).lower()
    if prompt and not any(term in prompt for term in ("untrusted", "instructions", "trusted")):
        add("medium", "Prompt trust boundary unclear", "system_prompt",
            "System prompt does not visibly describe how untrusted user or retrieved content is handled.",
            "Explicitly separate trusted instructions from untrusted input and retrieved documents.")
    if config.get("logging", {}).get("include_prompts") is True if isinstance(config.get("logging"), dict) else False:
        add("high", "Sensitive prompt logging enabled", "logging.include_prompts=true",
            "Full prompts may contain credentials or personal data.",
            "Disable raw prompt logging or apply strict redaction, access control, and retention limits.")

    weights = {"critical": 25, "high": 12, "medium": 6, "low": 2}
    risk = min(100, sum(weights.get(f["severity"], 0) for f in findings))
    return {
        "risk_score": risk,
        "risk_level": "critical" if risk >= 70 else "high" if risk >= 40 else "medium" if risk >= 15 else "low",
        "finding_count": len(findings),
        "findings": findings,
        "disclaimer": "Heuristic configuration review only; not a penetration test, certification, or compliance assessment."
    }

def audit_text(raw: str, filename: str = "config.json") -> dict[str, Any]:
    return audit_config(parse_config(raw, filename))
