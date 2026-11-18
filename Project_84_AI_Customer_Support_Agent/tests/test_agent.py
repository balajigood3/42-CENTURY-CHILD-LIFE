import json
import pytest
from support_agent.knowledge import DEFAULT_FAQS, load_faqs, search_faqs
from support_agent.agent import redact_sensitive, classify_intent, draft_response, create_ticket
from support_agent.storage import append_record, recent_records

def test_default_faqs_exist():
    assert len(load_faqs("missing/faqs.json")) >= 3

def test_faq_search_finds_order():
    result = search_faqs("where is my order tracking", DEFAULT_FAQS)
    assert result[0]["id"] == "FAQ-001"

def test_faq_search_empty():
    assert search_faqs("ok", DEFAULT_FAQS) == []

def test_load_invalid_json(tmp_path):
    p = tmp_path / "faqs.json"
    p.write_text("{invalid")
    with pytest.raises(ValueError):
        load_faqs(p)

def test_redacts_password_and_card_number():
    text = redact_sensitive("password=secret123 card 4111111111111111")
    assert "secret123" not in text
    assert "4111111111111111" not in text

def test_classifies_return_intent():
    assert classify_intent("I need a refund for my item") == "return_refund"

def test_draft_response_cites_faq():
    result = draft_response("Where is my order tracking?", DEFAULT_FAQS)
    assert result["citations"]
    assert result["confidence"] == "matched_faq"

def test_unknown_query_handoff():
    result = draft_response("Need assistance with an unusual problem", [])
    assert result["handoff_recommended"]
    assert result["citations"] == []

def test_short_message_rejected():
    with pytest.raises(ValueError):
        draft_response(" ", DEFAULT_FAQS)

def test_ticket_draft_status():
    ticket = create_ticket("CUST-001", "Package arrived damaged", "High")
    assert ticket["status"] == "OPEN_DRAFT"

def test_ticket_rejects_invalid_priority():
    with pytest.raises(ValueError):
        create_ticket("CUST-001", "Help", "Urgent")

def test_ticket_redacts_sensitive_content():
    ticket = create_ticket("CUST-001", "My password=abc123 is not working")
    assert "abc123" not in ticket["message"]

def test_storage_round_trip(tmp_path):
    p = tmp_path / "audit.jsonl"
    append_record(p, {"event": "query"})
    assert recent_records(p)[0]["event"] == "query"
