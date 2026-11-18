import json
import pytest
from devops_assistant.analyzer import analyze_compose, create_plan
from devops_assistant.generator import generate_artifacts

def test_flags_privileged_latest_and_missing_healthcheck():
    report = analyze_compose("""
services:
  app:
    image: demo:latest
    privileged: true
""")
    rules = {item["rule"] for item in report["findings"]}
    assert {"PIN_IMAGE_TAG", "PRIVILEGED", "HEALTHCHECK", "NON_ROOT_USER"} <= rules

def test_rejects_missing_services():
    with pytest.raises(ValueError):
        analyze_compose("name: empty")

def test_rejects_non_mapping_root():
    with pytest.raises(ValueError):
        analyze_compose("- item")

def test_flags_possible_secret():
    report = analyze_compose({"services": {"api": {"image": "api:v1",
                       "environment": {"PASSWORD": "password=abc"}}}})
    assert "POSSIBLE_SECRET" in {x["rule"] for x in report["findings"]}

def test_plan_has_safety_boundary():
    report = analyze_compose({"services": {"api": {"image": "api:v1", "user": "1000"}}})
    plan = create_plan(report)
    assert "does not deploy" in plan.lower()
    assert "approved CI/CD" in plan

def test_generates_artifacts(tmp_path):
    report = generate_artifacts("""services:\n  app:\n    image: app:v1\n""", tmp_path)
    assert report["service_count"] == 1
    for name in ("risk_report.json", "DEPLOYMENT_PLAN.md", "CHECKLIST.md", "Makefile"):
        assert (tmp_path / name).is_file()
    parsed = json.loads((tmp_path / "risk_report.json").read_text())
    assert parsed["service_count"] == 1
