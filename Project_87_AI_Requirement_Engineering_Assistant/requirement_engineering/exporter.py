import json
from pathlib import Path

def export_json(data, path):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(data, path):
    s = data["summary"]
    lines = ["# Requirements Analysis", "", "## Summary",
             f"- Total: {s['total']}", f"- Functional: {s['functional']}",
             f"- Non-functional: {s['non_functional']}",
             f"- Needs clarification: {s['needs_clarification']}",
             f"- Vague wording flags: {s['with_quality_flags']}", "", "## Requirements"]
    for req in data["requirements"]:
        lines += [f"### {req['id']} — {req['type']}", req["statement"],
                  f"- Actor: {req['actor']}", f"- Action: {req['action']}",
                  f"- Quality flags: {', '.join(req['quality_flags']) or 'None'}",
                  "- Clarification questions:"]
        lines += [f"  - {q}" for q in req["clarification_questions"]]
        lines += ["- Acceptance criteria:"] + [f"  - {x}" for x in req["acceptance_criteria"]]
    lines += ["", "## Traceability matrix", "| Requirement | Test case | Status |",
              "|---|---|---|"]
    lines += [f"| {x['requirement_id']} | {x['test_case_id']} | {x['test_status']} |"
              for x in data["traceability"]]
    lines += ["", f"> {data['disclaimer']}", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
