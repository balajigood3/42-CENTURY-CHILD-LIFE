import json
from pathlib import Path

def export_json(result, path):
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(result, path):
    lines = [f"# {result['meeting_title']}", "", f"**Date:** {result['meeting_date'] or 'Not provided'}",
             "", "## Summary"]
    lines += [f"- {x}" for x in result["summary"]]
    lines += ["", "## Decisions"]
    lines += [f"- {x}" for x in result["decisions"]] or ["- No decision markers detected."]
    lines += ["", "## Action items", "| Owner | Task | Status |", "|---|---|---|"]
    lines += [f"| {x['owner']} | {x['task']} | {x['status']} |" for x in result["action_items"]]
    lines += ["", "## Risks and blockers"]
    lines += [f"- {x}" for x in result["risks_and_blockers"]] or ["- No configured risk markers detected."]
    lines += ["", "## Key topics", ", ".join(result["key_topics"]), "", "## Follow-up questions"]
    lines += [f"- {x}" for x in result["follow_up_questions"]]
    lines += ["", f"> {result['disclaimer']}", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
