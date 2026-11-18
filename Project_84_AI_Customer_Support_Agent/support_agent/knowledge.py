"""Small editable FAQ knowledge base and keyword retrieval."""
import json
from pathlib import Path

DEFAULT_FAQS = [
    {"id": "FAQ-001", "category": "Orders", "question": "Where is my order?",
     "answer": "Use the order tracking page with your order number to view the latest status.",
     "keywords": ["order", "tracking", "delivery", "shipment"]},
    {"id": "FAQ-002", "category": "Returns", "question": "How can I return an item?",
     "answer": "Check the return policy and submit a return request with your order number and reason.",
     "keywords": ["return", "refund", "exchange", "item"]},
    {"id": "FAQ-003", "category": "Payments", "question": "Which payment methods are supported?",
     "answer": "Available payment methods are shown at checkout. Never share card PINs or one-time passwords with support.",
     "keywords": ["payment", "card", "checkout", "transaction"]},
    {"id": "FAQ-004", "category": "Account", "question": "How do I reset my password?",
     "answer": "Use the official password reset option on the sign-in page. Support will never ask for your current password.",
     "keywords": ["password", "login", "account", "reset"]},
    {"id": "FAQ-005", "category": "Support", "question": "How do I contact support?",
     "answer": "Submit a support ticket with a short description and a safe contact method. Do not include passwords or payment secrets.",
     "keywords": ["contact", "support", "ticket", "help"]}
]

def load_faqs(path="data/faqs.json"):
    file = Path(path)
    if not file.exists():
        return DEFAULT_FAQS.copy()
    try:
        items = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("FAQ file could not be read as valid JSON.") from exc
    if not isinstance(items, list):
        raise ValueError("FAQ file must contain a JSON list.")
    required = ("id", "category", "question", "answer", "keywords")
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict) or not all(k in item for k in required):
            raise ValueError(f"FAQ item {i} is missing required fields.")
        if not all(isinstance(item[k], str) and item[k].strip() for k in required[:4]):
            raise ValueError(f"FAQ item {i} has invalid text fields.")
        if not isinstance(item["keywords"], list) or not all(isinstance(x, str) for x in item["keywords"]):
            raise ValueError(f"FAQ item {i} keywords must be a list of strings.")
    return items

def search_faqs(query, faqs, limit=3):
    tokens = {x.lower() for x in query.split() if len(x) > 2}
    if not tokens:
        return []
    ranked = []
    for faq in faqs:
        haystack = " ".join([faq["category"], faq["question"], faq["answer"], *faq["keywords"]]).lower()
        score = sum(1 for token in tokens if token in haystack)
        if score:
            ranked.append((score, faq))
    ranked.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [item for _, item in ranked[:max(1, min(limit, 10))]]
