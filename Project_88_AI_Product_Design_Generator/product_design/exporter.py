import json
from pathlib import Path

def export_json(concept, path):
    Path(path).write_text(json.dumps(concept, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(concept, path):
    lines = [f"# Product Concept: {concept['product_name']}", "",
             f"**Domain:** {concept['domain']}  ",
             f"**Platform:** {concept['platform']}  ",
             f"**Target audience:** {concept['target_audience']}", "",
             "## Problem", concept["problem_statement"], "",
             "## Product vision", concept["product_vision"], "",
             "## Personas"]
    for p in concept["personas"]:
        lines += [f"### {p['name']}", p["description"], f"- Goal: {p['goal']}"]
    lines += ["", "## Feature backlog", "| ID | Feature | Priority | Release |",
              "|---|---|---|---|"]
    lines += [f"| {x['feature_id']} | {x['name']} | {x['priority']} | {x['release']} |"
              for x in concept["feature_backlog"]]
    lines += ["", "## MVP scope"] + [f"- {x}" for x in concept["mvp_scope"]]
    lines += ["", "## Requirements"]
    lines += [f"- **{x['id']} ({x['type']}, {x['priority']}):** {x['statement']}"
              for x in concept["requirements"]]
    lines += ["", "## Delivery roadmap"]
    for phase in concept["delivery_roadmap"]:
        lines += [f"### {phase['phase']}"] + [f"- {x}" for x in phase["deliverables"]]
    lines += ["", "## Success metrics"]
    lines += [f"- **{x['metric']}:** {x['definition']}" for x in concept["success_metrics"]]
    lines += ["", "## Risks and mitigations"]
    lines += [f"- **{x['risk']}:** {x['mitigation']}" for x in concept["risks_and_mitigations"]]
    lines += ["", "## Assumptions"] + [f"- {x}" for x in concept["assumptions"]]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
