import json
import zipfile
from pathlib import Path
from .analyzer import analyze_source, conservative_modernize

def export_bundle(source: str, output_path: str | Path, filename: str = "legacy.py") -> Path:
    result = analyze_source(source)
    report = {"input_file": filename, **result,
              "note": "Static advisory only. Review suggestions and run tests before adopting changes."}
    lines = ["# Legacy Code Modernization Report", "", f"**Input:** `{filename}`", "",
             f"**Findings:** {result['summary']['finding_count']}", "",
             "| Severity | Count |", "|---|---:|"]
    for level, count in result["summary"]["severity_counts"].items():
        lines.append(f"| {level} | {count} |")
    lines += ["", "## Findings", ""]
    for item in result["findings"]:
        lines += [f"### {item['rule']} — {item['severity']}", "",
                  f"Line {item['line']}: {item['message']}", "",
                  f"**Recommendation:** {item['recommendation']}", ""]
    if not result["findings"]:
        lines.append("No configured modernization patterns were detected.")
    lines += ["", "## Safety note", "", report["note"], ""]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("original.py", source)
        zf.writestr("modernized.py", conservative_modernize(source))
        zf.writestr("report.json", json.dumps(report, indent=2))
        zf.writestr("REPORT.md", "\n".join(lines))
    return output_path
