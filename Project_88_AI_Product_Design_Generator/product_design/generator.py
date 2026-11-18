"""Structured product concept generator using deterministic design heuristics."""
from __future__ import annotations
import re

FEATURE_LIBRARY = {
    "marketplace": ["Product catalog", "Search and filters", "Cart and checkout", "Order tracking", "Seller dashboard"],
    "finance": ["Account overview", "Transaction history", "Budget categories", "Spending alerts", "Exportable statements"],
    "education": ["Course catalog", "Learning progress", "Practice assessments", "Feedback and hints", "Instructor dashboard"],
    "health": ["Appointment scheduling", "Care information", "Reminder preferences", "Secure document access", "Provider dashboard"],
    "productivity": ["Task workspace", "Due dates and reminders", "Team collaboration", "Progress dashboard", "Activity history"],
    "generic": ["User onboarding", "Core workspace", "Search and filtering", "Notifications", "Analytics dashboard"]
}

def _clean(value, field, max_len=500):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text.")
    value = re.sub(r"\s+", " ", value).strip()
    if not value:
        raise ValueError(f"{field} is required.")
    if len(value) > max_len:
        raise ValueError(f"{field} must be {max_len} characters or fewer.")
    return value

def infer_domain(description):
    text = description.lower()
    keywords = {
        "marketplace": ("marketplace", "shopping", "ecommerce", "e-commerce", "seller", "buyer", "store"),
        "finance": ("finance", "bank", "budget", "payment", "expense", "money", "wallet"),
        "education": ("education", "learning", "course", "student", "teacher", "school", "training"),
        "health": ("health", "clinic", "hospital", "patient", "appointment", "medical"),
        "productivity": ("productivity", "task", "project", "team", "workflow", "work management")
    }
    for domain, terms in keywords.items():
        if any(term in text for term in terms):
            return domain
    return "generic"

def generate_product_concept(product_name, problem, audience, platform="Web",
                             constraints="", include_mvp=True):
    name = _clean(product_name, "Product name", 100)
    problem = _clean(problem, "Problem statement", 1500)
    if len(problem) < 15:
        raise ValueError("Problem statement must contain at least 15 characters.")
    audience = _clean(audience, "Target audience", 300)
    platform = _clean(platform, "Platform", 50)
    constraints = re.sub(r"\s+", " ", constraints).strip() if constraints else "Not specified"
    if len(constraints) > 1000:
        raise ValueError("Constraints must be 1000 characters or fewer.")

    domain = infer_domain(problem + " " + name)
    features = FEATURE_LIBRARY[domain]
    personas = [
        {"name": "Primary user", "description": audience,
         "goal": f"Complete the main task related to: {problem[:180]}"},
        {"name": "Administrator", "description": "Product operations or support owner",
         "goal": "Manage access, monitor usage and resolve operational issues"}
    ]
    requirements = [
        {"id": "PR-001", "type": "Functional", "priority": "Must",
         "statement": "The system shall allow a user to create and manage an account."},
        {"id": "PR-002", "type": "Functional", "priority": "Must",
         "statement": f"The system shall provide a workflow addressing: {problem[:220]}"},
        {"id": "PR-003", "type": "Non-functional", "priority": "Must",
         "statement": "The system shall enforce authenticated access and validate user input."},
        {"id": "PR-004", "type": "Non-functional", "priority": "Should",
         "statement": "The interface should support responsive layouts for the selected platform."}
    ]
    mvp = features[:3] if include_mvp else []
    phases = [
        {"phase": "Discovery", "deliverables": ["User interviews", "Problem validation", "Success metrics"]},
        {"phase": "MVP", "deliverables": mvp or ["Validate the smallest end-to-end user journey"]},
        {"phase": "Beta", "deliverables": ["Usability testing", "Analytics instrumentation", "Feedback prioritization"]},
        {"phase": "Launch", "deliverables": ["Operational readiness", "Support process", "Release monitoring"]}
    ]
    risks = [
        {"risk": "Problem-solution mismatch", "mitigation": "Validate the problem with target users before building."},
        {"risk": "Scope expansion", "mitigation": "Prioritize MVP outcomes and defer non-essential features."},
        {"risk": "Privacy or security gaps", "mitigation": "Complete threat modelling and privacy review before launch."},
        {"risk": "Low adoption", "mitigation": "Test onboarding and measure activation and retention."}
    ]
    success_metrics = [
        {"metric": "Activation rate", "definition": "New users completing the core onboarding or first-value action"},
        {"metric": "Task success rate", "definition": "Users completing the primary workflow successfully"},
        {"metric": "Retention", "definition": "Users returning within the chosen measurement window"},
        {"metric": "User satisfaction", "definition": "Survey-based satisfaction or usability score"}
    ]
    return {
        "product_name": name, "problem_statement": problem, "target_audience": audience,
        "platform": platform, "domain": domain, "constraints": constraints,
        "product_vision": f"Help {audience} solve the stated problem through a focused {platform.lower()} experience.",
        "personas": personas, "feature_backlog": [
            {"feature_id": f"F-{i:02d}", "name": feature,
             "priority": "Must" if i <= 3 else "Should",
             "release": "MVP" if i <= 3 else "Later"}
            for i, feature in enumerate(features, 1)
        ],
        "requirements": requirements, "mvp_scope": mvp,
        "delivery_roadmap": phases, "success_metrics": success_metrics,
        "risks_and_mitigations": risks,
        "assumptions": [
            "This is an initial concept draft generated from limited input.",
            "Feature priorities and roadmap are starting suggestions, not validated estimates.",
            "User research, technical feasibility and compliance reviews are still required."
        ]
    }

def validate_concept(data):
    required = {"product_name", "problem_statement", "target_audience", "platform",
                "domain", "product_vision", "personas", "feature_backlog",
                "requirements", "mvp_scope", "delivery_roadmap", "success_metrics",
                "risks_and_mitigations", "assumptions", "constraints"}
    if not isinstance(data, dict) or not required.issubset(data):
        raise ValueError("Product concept is missing required fields.")
    for key in ("product_name", "problem_statement", "target_audience", "platform", "domain", "product_vision"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"{key} must be a non-empty string.")
    for key in ("personas", "feature_backlog", "requirements", "mvp_scope",
                "delivery_roadmap", "success_metrics", "risks_and_mitigations", "assumptions"):
        if not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list.")
    feature_ids = [x.get("feature_id") for x in data["feature_backlog"]]
    if len(feature_ids) != len(set(feature_ids)):
        raise ValueError("Feature IDs must be unique.")
    return data
