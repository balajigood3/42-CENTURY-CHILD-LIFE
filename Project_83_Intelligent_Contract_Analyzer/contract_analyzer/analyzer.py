"""Heuristic contract review utilities. Not legal advice."""
from __future__ import annotations
import re
from datetime import date

CLAUSE_PATTERNS = {
    "termination": [r"\btermination\b", r"\bterminate\b", r"\bnotice period\b"],
    "confidentiality": [r"\bconfidential(?:ity)?\b", r"\bnon-disclosure\b"],
    "indemnity": [r"\bindemnif(?:y|ication)\b", r"\bhold harmless\b"],
    "limitation_of_liability": [r"\blimitation of liability\b", r"\bliability cap\b", r"\baggregate liability\b"],
    "payment": [r"\bpayment\b", r"\binvoice\b", r"\bnet\s+\d+\b", r"\blate fee\b"],
    "governing_law": [r"\bgoverning law\b", r"\bgoverned by the laws\b"],
    "dispute_resolution": [r"\barbitration\b", r"\bdispute resolution\b", r"\bmediation\b"],
    "data_protection": [r"\bpersonal data\b", r"\bdata protection\b", r"\bsecurity incident\b", r"\bdata breach\b"],
    "intellectual_property": [r"\bintellectual property\b", r"\bwork product\b", r"\bownership of\b"],
    "renewal": [r"\bauto(?:matic)? renewal\b", r"\brenewal\b", r"\brenew\b"],
    "force_majeure": [r"\bforce majeure\b", r"\bevents beyond.*control\b"],
    "warranty": [r"\bwarrant(?:y|ies)\b", r"\bas[- ]is\b"]
}

RISK_RULES = [
    ("termination", r"\bno termination\b|\bnon-cancellable\b", "High", "Termination may be restricted; verify exit rights and exceptions."),
    ("liability", r"\bno limit(?:ation)? of liability\b|\bunlimited liability\b", "High", "Potentially uncapped liability; assess caps and carve-outs."),
    ("indemnity", r"\bindemnif(?:y|ication)\b|\bhold harmless\b", "Medium", "Review indemnity scope, exclusions, procedure and liability interaction."),
    ("renewal", r"\bauto(?:matic)? renewal\b|\bautomatically renew", "Medium", "Check renewal term, notice window and cancellation method."),
    ("payment", r"\blate fee\b|\binterest at\b|\bpenalty\b", "Medium", "Review late-payment charges and whether they are clearly defined."),
    ("data", r"\bpersonal data\b|\bdata protection\b|\bdata breach\b", "High", "Confirm security obligations, breach notification and data-processing terms."),
    ("ip", r"\bintellectual property\b|\bwork product\b", "Medium", "Confirm ownership, license scope and rights to pre-existing materials."),
]

def extract_text_from_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to read PDF files: pip install pypdf") from exc
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_clauses(text):
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n|(?<=[.;])\s+(?=[A-Z])", text) if p.strip()]
    found = []
    for name, patterns in CLAUSE_PATTERNS.items():
        matches = []
        for paragraph in paragraphs:
            if any(re.search(pattern, paragraph, re.I) for pattern in patterns):
                matches.append(paragraph[:1200])
        if matches:
            found.append({"clause_type": name, "excerpts": matches[:8]})
    return found

def extract_metadata(text):
    parties = []
    for pattern in (
        r"(?:between|by and between)\s+([^,\n;]{2,100}?)\s+(?:and|&)\s+([^,\n;]{2,100}?)(?:,|\n|\.|$)",
        r"(?:the\s+)?(?:customer|client|vendor|supplier|company)\s*:\s*([^\n;]{2,100})"
    ):
        for match in re.finditer(pattern, text, re.I):
            if len(match.groups()) == 2:
                parties.extend([match.group(1).strip(), match.group(2).strip()])
            else:
                parties.append(match.group(1).strip())
    parties = list(dict.fromkeys(p for p in parties if p))
    dates = sorted(set(re.findall(
        r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"January|February|March|April|May|June|July|August|September|October|November|December"
        r"\s+\d{1,2},?\s+\d{4})\b", text, re.I)))
    return {"possible_parties": parties[:10], "date_strings": dates[:30]}

def identify_risks(text):
    risks = []
    for category, pattern, severity, explanation in RISK_RULES:
        matches = list(re.finditer(pattern, text, re.I))
        if matches:
            excerpt = text[max(0, matches[0].start()-100):min(len(text), matches[0].end()+180)]
            risks.append({"category": category, "severity": severity,
                          "observation": explanation, "evidence_excerpt": re.sub(r"\s+", " ", excerpt).strip()})
    return risks

def analyze_contract(text, filename="pasted_contract.txt"):
    if not isinstance(text, str) or len(text.strip()) < 30:
        raise ValueError("Contract text must contain at least 30 characters.")
    if len(text) > 200_000:
        raise ValueError("Contract text exceeds the 200,000 character demo limit.")
    clauses = extract_clauses(text)
    risks = identify_risks(text)
    metadata = extract_metadata(text)
    found_types = {item["clause_type"] for item in clauses}
    missing = [name for name in ("termination", "confidentiality", "limitation_of_liability",
                                  "governing_law", "dispute_resolution", "data_protection")
               if name not in found_types]
    return {
        "filename": filename,
        "character_count": len(text),
        "metadata": metadata,
        "clauses": clauses,
        "risk_flags": risks,
        "clauses_not_detected": missing,
        "review_checklist": [
            "Confirm the correct legal entities, signatories and effective date.",
            "Check scope, deliverables, acceptance criteria and service levels.",
            "Review payment, taxes, expenses and late-payment provisions.",
            "Review termination, renewal, notice periods and transition assistance.",
            "Review confidentiality, privacy, security and breach notification.",
            "Review intellectual property ownership and license rights.",
            "Check indemnities, liability caps, exclusions and insurance.",
            "Confirm governing law, venue and dispute-resolution process."
        ],
        "disclaimer": "Automated issue-spotting only; not legal advice. Clause detection can miss context, negation, exceptions and cross-references. Have qualified counsel review the full agreement."
    }
