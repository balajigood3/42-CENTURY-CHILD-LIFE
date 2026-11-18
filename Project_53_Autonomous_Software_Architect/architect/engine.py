from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from io import BytesIO
from pathlib import PurePosixPath
import re
from zipfile import ZipFile, ZIP_DEFLATED

@dataclass(frozen=True)
class ArchitectureInput:
    name: str
    slug: str
    brief: str
    scale: str
    sensitivity: str
    availability: str

def slugify(value: str) -> str:
    if "/" in value or "\\" in value or ".." in value:
        raise ValueError("Project name cannot contain path traversal characters.")
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Project name must contain letters or numbers.")
    return slug[:50]

def validate_input(name: str, brief: str, scale: str, sensitivity: str, availability: str) -> ArchitectureInput:
    if not name.strip():
        raise ValueError("Project name is required.")
    if len(brief.strip()) < 25:
        raise ValueError("Please provide a more detailed brief (at least 25 characters).")
    if len(brief) > 12000:
        raise ValueError("Brief must be 12,000 characters or fewer.")
    if scale not in {"small", "medium", "large"}:
        raise ValueError("Unsupported scale.")
    if sensitivity not in {"public", "internal", "sensitive"}:
        raise ValueError("Unsupported data sensitivity.")
    if availability not in {"standard", "high"}:
        raise ValueError("Unsupported availability target.")
    return ArchitectureInput(name.strip(), slugify(name), brief.strip(), scale, sensitivity, availability)

def _detect(brief: str) -> list[str]:
    text = brief.lower()
    candidates = [
        ("authentication", ("login", "auth", "user account", "identity")),
        ("payments", ("payment", "billing", "invoice", "subscription")),
        ("file storage", ("upload", "document", "file", "attachment")),
        ("search", ("search", "filter", "catalog")),
        ("notifications", ("notification", "email", "sms", "reminder")),
        ("analytics", ("analytics", "report", "dashboard", "metrics")),
        ("real-time updates", ("real-time", "realtime", "live update", "websocket")),
        ("workflow orchestration", ("approval", "workflow", "review process")),
    ]
    found = [label for label, terms in candidates if any(term in text for term in terms)]
    return found or ["core business workflow"]

def create_architecture(name: str, brief: str, scale: str = "small",
                        sensitivity: str = "internal", availability: str = "standard") -> dict[str, str]:
    spec = validate_input(name, brief, scale, sensitivity, availability)
    modules = _detect(spec.brief)
    if spec.scale == "small":
        topology = "Modular monolith"
        app_nodes = "API[FastAPI modular API]"
    elif spec.scale == "medium":
        topology = "Modular monolith with background worker"
        app_nodes = "API[FastAPI modular API]\\nWorker[Background worker]"
    else:
        topology = "Domain-oriented services (split only where independently scaled)"
        app_nodes = "Gateway[API gateway]\\nServices[Domain services]\\nWorker[Async workers]"
    db = "Managed PostgreSQL with encrypted backups" if spec.sensitivity == "sensitive" else "PostgreSQL"
    cache = "Redis cache / queue" if spec.scale != "small" or spec.availability == "high" else "Optional Redis when justified"
    auth = "OIDC/OAuth 2.1, short-lived access tokens, role and resource-level authorization"
    if spec.sensitivity == "sensitive":
        data_controls = "- Encrypt transport and storage; manage keys separately\\n- Minimize and classify personal data\\n- Audit sensitive reads and writes\\n- Define retention, deletion, backup, and restore policies\\n- Never place secrets or sensitive records in logs"
    else:
        data_controls = "- TLS for network traffic and encryption at rest where supported\\n- Restrict database and object-store access\\n- Define retention and backup policies\\n- Redact credentials and personal data from logs"
    module_lines = "\\n".join(f"- **{m.title()}** — isolate behind a clear service/module interface." for m in modules)
    mermaid = f"""flowchart LR
    U[Web / Mobile Client] --> CDN[CDN / Static Hosting]
    CDN --> API[HTTPS API]
    subgraph Application
    {app_nodes}
    end
    API --> API
    API --> DB[( {db} )]
    API --> CACHE[{cache}]
    Worker --> QUEUE[(Job Queue)]:::optional
    CACHE --> OBS[Logs / Metrics / Traces]
    API --> OBS
    classDef optional stroke-dasharray: 5 5
"""
    architecture = f"""# {spec.name} — Architecture Proposal

## Executive summary
**Recommended topology:** {topology}.

This proposal is generated from the supplied brief using transparent heuristics. It is a starting design and requires review by the delivery team.

## Problem statement
{spec.brief}

## Context and assumptions
- Expected scale: **{spec.scale}**
- Data sensitivity: **{spec.sensitivity}**
- Availability target: **{spec.availability}**
- Primary client: browser-based web client; add mobile clients only if required.
- API style: versioned REST/JSON unless event-driven integration is a confirmed requirement.

## Proposed technology baseline
| Layer | Recommendation | Rationale |
|---|---|---|
| Frontend | React + TypeScript | Component-based UI and typed contracts |
| Backend | Python + FastAPI | Typed request validation and OpenAPI |
| Database | {db} | Relational integrity and transactions |
| Cache / queue | {cache} | Add only for measured latency or async workload |
| Authentication | {auth} | Centralized identity and authorization |
| Observability | Structured logs, metrics, traces | Operational diagnosis |

## Logical modules
{module_lines}

## Key design decisions
1. Start with **{topology}**; avoid premature microservice boundaries.
2. Keep domain logic out of HTTP controllers.
3. Use database migrations and explicit transaction boundaries.
4. Treat background work as retryable and idempotent.
5. Publish and version API contracts.

## Quality attributes
- Reliability: health/readiness checks, bounded retries, backups, restore drills.
- Performance: pagination, indexes, connection pooling, measured caching.
- Maintainability: modular boundaries, code ownership, automated tests.
- Security: least privilege, centralized secrets, audit trails.
- Accessibility: keyboard navigation and semantic UI controls.

## Risks and open questions
- Confirm actual traffic, peak concurrency, data residency, RPO/RTO, and budget.
- Confirm integrations, regulatory obligations, and retention requirements.
- Validate the topology with a workload model before production deployment.

## Generated on
{date.today().isoformat()}
"""
    requirements = f"""# Requirements and Acceptance Criteria

## Functional requirements inferred from brief
{chr(10).join(f"- The system shall support the {m} capability where confirmed by product discovery." for m in modules)}
- The system shall expose documented, versioned APIs.
- The system shall validate input and return consistent error responses.
- The system shall support authorized CRUD operations for approved domain resources.

## Non-functional requirements
- Availability: {spec.availability} target; define numeric SLO before implementation.
- Scale: {spec.scale}; validate using realistic load tests.
- Data classification: {spec.sensitivity}; see security review.
- Observability: correlation IDs, structured logs, metrics, and traces.
- Recovery: document RPO/RTO and test backup restoration.

## Acceptance checklist
- [ ] Product owner approves user journeys and edge cases.
- [ ] API contract and data model reviewed.
- [ ] Unit, integration, and end-to-end tests pass.
- [ ] Authorization tests cover role and resource boundaries.
- [ ] Load test meets agreed SLO.
- [ ] Backup restore and failure recovery demonstrated.
- [ ] Accessibility and security reviews completed.
"""
    security = f"""# Security Review Checklist

## Baseline controls
- [ ] Use {auth}.
- [ ] Enforce authorization server-side on every protected resource.
- [ ] Validate and normalize untrusted input; use parameterized queries.
- [ ] Apply rate limits, request-size limits, and abuse monitoring.
- [ ] Store secrets in a managed secret store; rotate credentials.
- [ ] Pin and scan dependencies and container images.
- [ ] Use secure headers, strict CORS allowlists, and TLS.
- [ ] Keep audit events for privileged and sensitive operations.
- [ ] Test authentication, authorization, injection, and dependency risks.

## Data controls
{data_controls}

## Threat-model prompts
- What happens if an account is compromised?
- Can one tenant or user access another user's records?
- Which external integrations receive data?
- What is the incident response and breach notification process?

## Review status
This is a checklist, not a security certification. A qualified reviewer must validate the implementation and applicable legal requirements.
"""
    deployment = f"""# Deployment and Operations Plan

## Environments
1. Local development with seeded non-sensitive data.
2. Staging matching production topology.
3. Production with controlled release and rollback.

## Build and release
- Build immutable frontend and backend artifacts.
- Run linting, unit tests, integration tests, dependency scanning, and image scanning.
- Apply database migrations as a controlled release step.
- Deploy progressively; monitor error rate and latency before full rollout.

## Runtime
- Containerize API and worker processes.
- Configure health and readiness endpoints.
- Use managed PostgreSQL; use {cache} only when needed.
- Store secrets outside source control.
- Configure centralized logs, metrics, traces, and alert routing.

## Reliability
- Define numeric SLO, RPO, and RTO with stakeholders.
- Use bounded retries with exponential backoff and jitter.
- Add idempotency for retryable writes and jobs.
- Schedule backups and test restoration regularly.

## Scale-specific note
For **{spec.scale}** scale, begin with the recommended topology in `ARCHITECTURE.md`; measure bottlenecks before introducing additional services.
"""
    api_contract = """# API Contract Starter

Use `/api/v1` as the versioned prefix. Replace example resources and schemas with domain-approved definitions.

| Method | Path | Purpose | Expected status |
|---|---|---|---|
| GET | `/api/v1/health` | Liveness | 200 |
| GET | `/api/v1/resources` | List with pagination | 200 |
| POST | `/api/v1/resources` | Create resource | 201 |
| GET | `/api/v1/resources/{id}` | Retrieve resource | 200 / 404 |
| PATCH | `/api/v1/resources/{id}` | Partial update | 200 / 404 |
| DELETE | `/api/v1/resources/{id}` | Delete resource | 204 / 404 |

All protected routes require authentication and server-side authorization. Standardize error payloads, pagination, idempotency, and request correlation.
"""
    adr = """# ADR-001: Start with a modular application boundary

- **Status:** Proposed
- **Context:** Initial scope and traffic profile are not yet fully measured.
- **Decision:** Begin with a modular monolith for small/medium scope; split independently deployed services only when ownership, scaling, or isolation requires it.
- **Consequences:** Simpler local development and transactions; modules must maintain strict boundaries to prevent coupling.
- **Revisit when:** Independent scaling, deployment cadence, team ownership, or fault isolation justifies service extraction.
"""
    return {
        "ARCHITECTURE.md": architecture,
        "architecture.mmd": mermaid,
        "requirements.md": requirements,
        "security-review.md": security,
        "deployment-plan.md": deployment,
        "api-contract.md": api_contract,
        "adr/ADR-001-modular-boundary.md": adr,
        "input/project-brief.txt": spec.brief,
        "README.md": f"# {spec.name} architecture pack\\n\\nGenerated by Autonomous Software Architect. Review all assumptions before implementation.\\n",
    }

def bundle_zip(files: dict[str, str]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe archive path.")
            archive.writestr(str(path), content)
    return buffer.getvalue()
