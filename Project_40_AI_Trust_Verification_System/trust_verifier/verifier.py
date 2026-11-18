"""Evidence-based trust assessment for claims and source metadata."""
from __future__ import annotations
import re
from urllib.parse import urlparse

TRUSTED_DOMAINS = {
    "who.int": "international health authority",
    "un.org": "international organization",
    "nist.gov": "standards authority",
    "cisa.gov": "cybersecurity authority",
    "data.gov": "government open data",
}
SUSPICIOUS_PATTERNS = [
    ("absolute_claim", re.compile(r"(?i)\b(guaranteed|100% accurate|always true|never fails)\b")),
    ("urgency_pressure", re.compile(r"(?i)\b(act now|urgent|limited time|immediately send)\b")),
    ("unsupported_authority", re.compile(r"(?i)\b(experts say|studies prove|scientists confirm)\b")),
]

def normalize_domain(url: str) -> str:
    parsed = urlparse(url if "://" in url else "https://" + url)
    host = (parsed.hostname or "").lower().strip(".")
    return host[4:] if host.startswith("www.") else host

def assess_source(source: dict) -> dict:
    url = str(source.get("url", "")).strip()
    title = str(source.get("title", "")).strip()
    publisher = str(source.get("publisher", "")).strip()
    domain = normalize_domain(url) if url else ""
    matched = next((d for d in TRUSTED_DOMAINS if domain == d or domain.endswith("." + d)), None)
    flags = []
    if not url:
        flags.append("missing_source_url")
    if not title:
        flags.append("missing_title")
    if url and not domain:
        flags.append("invalid_source_url")
    if matched:
        level = "recognized_domain"
        note = f"Domain matches a configured reference list: {TRUSTED_DOMAINS[matched]}."
    elif url:
        level = "unverified_domain"
        note = "Domain is not in the local reference list; this does not mean it is malicious."
    else:
        level = "no_source"
        note = "No source URL was provided."
    return {
        "title": title or "Untitled source",
        "publisher": publisher or "Unknown publisher",
        "url": url,
        "domain": domain,
        "domain_status": level,
        "flags": flags,
        "note": note,
        "verification_limit": "Domain matching is not proof of authenticity, current ownership, or claim accuracy."
    }

def assess_claim(claim: str, sources: list[dict]) -> dict:
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("Claim must be a non-empty string.")
    if not isinstance(sources, list):
        raise TypeError("Sources must be a list.")
    assessed = [assess_source(s) for s in sources if isinstance(s, dict)]
    flags = [name for name, pattern in SUSPICIOUS_PATTERNS if pattern.search(claim)]
    recognized = sum(s["domain_status"] == "recognized_domain" for s in assessed)
    unverified = sum(s["domain_status"] == "unverified_domain" for s in assessed)
    if not assessed:
        status = "unsupported"
    elif recognized:
        status = "has_recognized_source"
    elif unverified:
        status = "sources_unverified"
    else:
        status = "weak_source_metadata"
    score = min(100, (0 if recognized else 25) + (20 if not assessed else 0) + 10*len(flags) + 10*unverified)
    return {
        "claim": claim,
        "assessment": status,
        "risk_score": score,
        "claim_flags": flags,
        "source_count": len(assessed),
        "sources": assessed,
        "recommendation": "Seek independent corroboration and inspect the original source before relying on this claim.",
        "disclaimer": "This tool checks metadata and wording heuristics only. It does not verify factual truth or browse the cited pages."
    }

def assess_text(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")
    flags = [name for name, pattern in SUSPICIOUS_PATTERNS if pattern.search(text)]
    return {"flags": flags, "absolute_claims_detected": bool(flags), "note": "Wording flags are review signals, not proof of misinformation."}
