"""Rule-based legal document triage. Not legal advice or legal interpretation."""
import re
from collections import Counter

CLAUSE_PATTERNS = {
    "termination": (r"\bterminat(?:e|ion|ed)\b", "Termination", "Check notice period, termination rights, and post-termination duties."),
    "indemnity": (r"\bindemn(?:ity|if(?:y|ication))\b", "Indemnity", "Review scope, exclusions, caps, and third-party claim procedure."),
    "liability": (r"\bliabilit(?:y|ies)\b", "Liability", "Check liability cap, excluded losses, and exceptions."),
    "confidentiality": (r"\bconfidential(?:ity)?\b", "Confidentiality", "Review definition, permitted disclosures, and survival period."),
    "governing_law": (r"governing law|jurisdiction", "Governing law / jurisdiction", "Confirm governing law, courts, and dispute resolution venue."),
    "payment": (r"\bpayment\b|\binvoice\b|\bfee\b", "Payment", "Check amount, due date, taxes, late fees, and invoicing requirements."),
    "renewal": (r"\bauto(?:matic)? renewal\b|\brenewal\b", "Renewal", "Check renewal term, opt-out deadline, and notice method."),
    "data_protection": (r"personal data|data protection|privacy", "Data protection", "Review permitted processing, security, breach notice, and retention."),
    "intellectual_property": (r"intellectual property|ownership of work|copyright", "Intellectual property", "Confirm ownership, license scope, and rights to pre-existing materials."),
}

def analyze_document(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Document text is empty.")
    findings = []
    lower = text.lower()
    for key, (pattern, label, guidance) in CLAUSE_PATTERNS.items():
        matches = list(re.finditer(pattern, lower, flags=re.IGNORECASE))
        if matches:
            snippets = []
            for match in matches[:3]:
                start, end = max(0, match.start() - 100), min(len(text), match.end() + 180)
                snippets.append(text[start:end].replace("\n", " ").strip())
            findings.append({"clause": key, "label": label, "mentions": len(matches),
                             "review_guidance": guidance, "snippets": snippets})
    words = re.findall(r"\b[\w'-]+\b", text.lower())
    return {
        "character_count": len(text),
        "word_count": len(words),
        "clause_findings": findings,
        "missing_common_clauses": [key for key in CLAUSE_PATTERNS if not any(f["clause"] == key for f in findings)],
        "disclaimer": "Automated issue-spotting only. This is not legal advice, does not determine enforceability, and may miss clauses or context."
    }

def build_report(report: dict, filename: str) -> str:
    lines = [f"# Legal Document Review — {filename}", "",
             "> Preliminary automated issue-spotting only; not legal advice.", "",
             f"- Characters: {report['character_count']}",
             f"- Words: {report['word_count']}", "",
             "## Detected clause topics", ""]
    if not report["clause_findings"]:
        lines.append("No supported clause patterns were detected.")
    for item in report["clause_findings"]:
        lines += [f"### {item['label']} ({item['mentions']} mention(s))",
                  item["review_guidance"], ""]
        for snippet in item["snippets"]:
            lines.append(f"> {snippet}")
            lines.append("")
    lines += ["## Common topics not detected", ""]
    lines += [f"- {key.replace('_', ' ').title()}" for key in report["missing_common_clauses"]]
    lines += ["", "## Review checklist",
              "- [ ] Confirm document parties, dates, and defined terms",
              "- [ ] Review clause language in full context",
              "- [ ] Check schedules, annexes, and cross-references",
              "- [ ] Ask a qualified lawyer about material risks",
              "", "## Disclaimer", report["disclaimer"]]
    return "\n".join(lines) + "\n"
