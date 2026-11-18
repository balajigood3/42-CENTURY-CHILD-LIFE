import json
import pytest
from enterprise_assistant.assistant import (
    load_documents, retrieve_documents, build_prompt, validate_response,
    create_action_request
)
from enterprise_assistant.storage import save_record, load_records

def docs():
    return [
        {"id": "HR-1", "title": "Leave", "department": "HR", "content": "Submit leave request to manager."},
        {"id": "IT-1", "title": "Password", "department": "IT", "content": "Use MFA and never share passwords."}
    ]

def test_load_default_docs(tmp_path):
    assert len(load_documents(tmp_path / "missing.json")) == 3

def test_load_invalid_knowledge_file(tmp_path):
    p = tmp_path / "knowledge.json"
    p.write_text("{bad", encoding="utf-8")
    with pytest.raises(ValueError):
        load_documents(p)

def test_retrieval_department_filter():
    assert retrieve_documents("leave request", docs(), "HR")[0]["id"] == "HR-1"

def test_retrieval_empty_question_rejected():
    with pytest.raises(ValueError):
        retrieve_documents(" ", docs())

def test_prompt_marks_reference_data_untrusted():
    prompt = build_prompt("How do I request leave?", docs(), "Employee")
    assert "untrusted reference data" in prompt

def test_invalid_role_rejected():
    with pytest.raises(ValueError):
        build_prompt("Question", docs(), "Guest")

def test_response_citations_must_be_retrieved():
    response = {"answer": "Answer", "citations": ["FAKE"],
                "follow_up_questions": [], "action_suggestion": ""}
    with pytest.raises(ValueError):
        validate_response(response, {"HR-1"})

def test_valid_response():
    response = {"answer": "Submit it to your manager.", "citations": ["HR-1"],
                "follow_up_questions": ["Which dates?"], "action_suggestion": ""}
    assert validate_response(response, {"HR-1"})["citations"] == ["HR-1"]

def test_action_is_pending_approval():
    request = create_action_request("Leave request", "Two days leave", "emp-01", "Employee")
    assert request["status"] == "PENDING_APPROVAL"

def test_unsupported_action_rejected():
    with pytest.raises(ValueError):
        create_action_request("Delete account", "Details", "emp-01", "IT Admin")

def test_storage_round_trip(tmp_path):
    p = tmp_path / "audit.jsonl"
    save_record(p, {"event": "query", "role": "Employee"})
    assert load_records(p)[0]["event"] == "query"

def test_storage_limit(tmp_path):
    p = tmp_path / "audit.jsonl"
    for i in range(3):
        save_record(p, {"event": str(i)})
    assert len(load_records(p, 2)) == 2
