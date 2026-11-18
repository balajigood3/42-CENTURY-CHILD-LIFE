"""Customer support response and ticket utilities."""
import re
from .knowledge import search_faqs

SENSITIVE_PATTERNS = [
    re.compile(r"\b(?:\d{13,19})\b"),
    re.compile(r"\b\d{3,4}\b"),
    re.compile(r"\b(?:password|passwd)\s*[:=]\s*\S+", re.I),
    re.compile(r"\b(?:otp|one[- ]time password)\s*[:=]?\s*\d{4,8}\b", re.I),
]

def redact_sensitive(text):
    cleaned = text
    for pattern in SENSITIVE_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    return cleaned

def classify_intent(message):
    text = message.lower()
    mapping = {
        "order_status": ("order", "tracking", "delivery", "shipment"),
        "return_refund": ("return", "refund", "exchange"),
        "payment": ("payment", "paid", "transaction", "billing"),
        "account_access": ("password", "login", "sign in", "account"),
        "human_support": ("agent", "human", "representative", "complaint")
    }
    scores = {intent: sum(1 for word in words if word in text)
              for intent, words in mapping.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "general"

def draft_response(message, faqs):
    if not isinstance(message, str) or len(message.strip()) < 3:
        raise ValueError("Please enter a support message with at least 3 characters.")
    safe_message = redact_sensitive(message.strip())
    intent = classify_intent(safe_message)
    matches = search_faqs(safe_message, faqs)
    if matches:
        top = matches[0]
        answer = top["answer"]
        citations = [item["id"] for item in matches]
        confidence = "matched_faq"
    else:
        answer = ("I could not find a verified answer in the support knowledge base. "
                  "Please create a support ticket or contact a human support representative.")
        citations = []
        confidence = "no_match"
    if intent == "human_support":
        answer = "I can help prepare a ticket, but a human support representative must handle this request."
    return {
        "intent": intent, "safe_message": safe_message, "answer": answer,
        "citations": citations, "confidence": confidence,
        "handoff_recommended": intent == "human_support" or not matches,
        "disclaimer": "This is an automated draft. Verify account-specific details with an authorized support representative."
    }

def create_ticket(customer_ref, message, priority="Normal"):
    if not customer_ref.strip() or len(customer_ref) > 80:
        raise ValueError("Provide a valid customer reference (not a password or secret).")
    if priority not in {"Low", "Normal", "High"}:
        raise ValueError("Unsupported ticket priority.")
    if not message.strip() or len(message) > 3000:
        raise ValueError("Ticket message must contain 1–3000 characters.")
    return {
        "customer_ref": customer_ref.strip(),
        "message": redact_sensitive(message.strip()),
        "priority": priority,
        "status": "OPEN_DRAFT",
        "notice": "Draft ticket only; it has not been sent to an external support system."
    }
