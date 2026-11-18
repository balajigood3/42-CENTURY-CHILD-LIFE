from pathlib import Path
import json
from .analyzer import analyze_compose, create_plan

def generate_artifacts(compose_text: str, output_dir: str | Path) -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = analyze_compose(compose_text)
    (output / "risk_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "DEPLOYMENT_PLAN.md").write_text(create_plan(report), encoding="utf-8")
    checklist = """# Deployment Checklist

- [ ] Review all CRITICAL and HIGH findings
- [ ] Confirm image tags/digests and provenance
- [ ] Verify secrets are externalized
- [ ] Confirm non-root execution and least privilege
- [ ] Confirm healthchecks and resource limits
- [ ] Run tests and configuration validation
- [ ] Review change diff and obtain approval
- [ ] Deploy using approved CI/CD workflow
- [ ] Verify health and rollback readiness
"""
    (output / "CHECKLIST.md").write_text(checklist, encoding="utf-8")
    (output / "Makefile").write_text(
        ".PHONY: test analyze\n"
        "test:\n\tpython -m pytest -q\n"
        "analyze:\n\tpython -m devops_assistant.cli sample-compose.yml --output generated\n",
        encoding="utf-8")
    return report
