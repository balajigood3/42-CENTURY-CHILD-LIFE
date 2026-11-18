"""Bounded, rule-based DevOps configuration analyzer. Never executes user commands."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def _load_config(source: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(source, dict):
        return source
    try:
        import yaml
        data = yaml.safe_load(source)
    except Exception as exc:
        raise ValueError(f"Invalid YAML/JSON configuration: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a mapping/object.")
    return data

def analyze_compose(source: str | dict[str, Any]) -> dict[str, Any]:
    data = _load_config(source)
    services = data.get("services")
    if not isinstance(services, dict) or not services:
        raise ValueError("Compose configuration must contain a non-empty 'services' mapping.")
    findings = []
    for name, service in services.items():
        if not isinstance(service, dict):
            findings.append({"severity": "HIGH", "service": str(name), "rule": "SERVICE_SHAPE",
                             "message": "Service definition must be a mapping."})
            continue
        image = service.get("image")
        if not image and not service.get("build"):
            findings.append({"severity": "HIGH", "service": name, "rule": "IMAGE_OR_BUILD",
                             "message": "Specify an image or build context."})
        if isinstance(image, str) and (image.endswith(":latest") or ":" not in image):
            findings.append({"severity": "MEDIUM", "service": name, "rule": "PIN_IMAGE_TAG",
                             "message": "Use an explicit, reviewed image tag or digest instead of latest/implicit tags."})
        if not service.get("healthcheck"):
            findings.append({"severity": "MEDIUM", "service": name, "rule": "HEALTHCHECK",
                             "message": "Consider adding a healthcheck for reliable service monitoring."})
        if not service.get("restart"):
            findings.append({"severity": "LOW", "service": name, "rule": "RESTART_POLICY",
                             "message": "Consider an explicit restart policy."})
        if service.get("privileged") is True:
            findings.append({"severity": "CRITICAL", "service": name, "rule": "PRIVILEGED",
                             "message": "Privileged containers substantially expand host access."})
        if service.get("user") in (None, "", "0", "root"):
            findings.append({"severity": "HIGH", "service": name, "rule": "NON_ROOT_USER",
                             "message": "Set a non-root runtime user where supported."})
        if service.get("environment") and isinstance(service["environment"], (dict, list)):
            env_text = json.dumps(service["environment"]).lower()
            if any(token in env_text for token in ("password=", "secret=", "api_key=", "token=")):
                findings.append({"severity": "CRITICAL", "service": name, "rule": "POSSIBLE_SECRET",
                                 "message": "Possible secret in environment values; use a secret manager or protected secret file."})
        if service.get("ports"):
            findings.append({"severity": "LOW", "service": name, "rule": "EXPOSED_PORTS",
                             "message": "Review published ports and bind to localhost when public access is unnecessary."})
        if not service.get("read_only"):
            findings.append({"severity": "LOW", "service": name, "rule": "READ_ONLY_FS",
                             "message": "Consider read_only: true with explicit writable tmpfs/volumes."})
        if not service.get("deploy", {}).get("resources") if isinstance(service.get("deploy", {}), dict) else True:
            findings.append({"severity": "LOW", "service": name, "rule": "RESOURCE_LIMITS",
                             "message": "Consider CPU and memory limits appropriate to the runtime."})
    counts = {level: sum(1 for item in findings if item["severity"] == level)
              for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    return {"service_count": len(services), "finding_count": len(findings),
            "severity_counts": counts, "findings": findings,
            "disclaimer": "Static checks only; review findings before changing any environment."}

def create_plan(report: dict[str, Any]) -> str:
    lines = ["# Deployment Review Plan", "",
             "This plan is generated from static configuration checks. It does not deploy or modify infrastructure.", "",
             "## Findings", ""]
    if not report["findings"]:
        lines.append("No configured rules were triggered. This is not a security certification.")
    for item in report["findings"]:
        lines.append(f"- **{item['severity']} — {item['service']} / {item['rule']}:** {item['message']}")
    lines += ["", "## Suggested execution sequence",
              "1. Review CRITICAL and HIGH findings with the service owner.",
              "2. Update configuration in a development branch.",
              "3. Run the project's tests and configuration validation.",
              "4. Review the diff and obtain required approval.",
              "5. Deploy through your organization's approved CI/CD process.",
              "", "## Safety boundary",
              "No cloud credentials are requested. No shell commands, deployments, or production changes are executed."]
    return "\n".join(lines) + "\n"
