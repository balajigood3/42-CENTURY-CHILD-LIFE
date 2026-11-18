import json
from pathlib import Path

def export_json(result, path):
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(result, path):
    m = result["metadata"]
    lines = [f"# Contract Review: {result['filename']}", "",
             f"Characters analyzed: {result['character_count']}", "",
             "## Possible metadata", f"- Parties: {', '.join(m['possible_parties']) or 'Not detected'}",
             f"- Dates: {', '.join(m['date_strings']) or 'Not detected'}", "", "## Detected clauses"]
    for clause in result["clauses"]:
        lines += [f"### {clause['clause_type'].replace('_', ' ').title()}"]
        lines += [f"- {x}" for x in clause["excerpts"]]
    lines += ["", "## Risk flags"]
    for risk in result["risk_flags"]:
        lines.append(f"- **{risk['severity']} — {risk['category']}**: {risk['observation']}")
        lines.append(f"  - Evidence: {risk['evidence_excerpt']}")
    lines += ["", "## Clauses not detected"]
    lines += [f"- {x}" for x in result["clauses_not_detected"]]
    lines += ["", "## Review checklist"]
    lines += [f"- [ ] {x}" for x in result["review_checklist"]]
    lines += ["", f"> Disclaimer: {result['disclaimer']}", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
