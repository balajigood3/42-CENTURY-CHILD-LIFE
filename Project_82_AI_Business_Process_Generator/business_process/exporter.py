import json
from pathlib import Path

def export_json(process, path):
    Path(path).write_text(json.dumps(process, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(process, path):
    lines = [f"# {process['process_name']}", "", f"**Objective:** {process['objective']}", "",
             "## Input description", process["source_description"], "", "## Stakeholders"]
    lines += [f"- {x}" for x in process["stakeholders"]]
    lines += ["", "## Workflow steps"]
    for step in process["steps"]:
        lines.append(f"- **{step['id']} — {step['name']}** ({step['owner']}, {step['type']}): {step['description']}")
    lines += ["", "## Risks and controls"]
    for item in process["risks_and_controls"]:
        lines.append(f"- **{item['risk']}** ({item['severity']}): {item['control']}")
    lines += ["", "## KPIs"]
    for item in process["kpis"]:
        lines.append(f"- **{item['name']}** ({item['unit']}): {item['definition']}")
    lines += ["", "## Mermaid flowchart", "```mermaid", process["mermaid_flowchart"], "```", "",
              "## Assumptions"]
    lines += [f"- {x}" for x in process["assumptions"]]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
