import pytest
from app.core import parse_json_response,lexical_similarity,heuristic_candidates,report_markdown
def test_fenced_json(): assert parse_json_response('```json\\n{"ok":true}\\n```')=={"ok":True}
def test_embedded_json(): assert parse_json_response('Result: {"x":2} done')=={"x":2}
def test_invalid_json():
    with pytest.raises(ValueError): parse_json_response("nothing")
def test_similarity(): assert lexical_similarity("Revenue was 10 million","Revenue was 12 million")>.4
def test_candidate():
    c=[{"claim":"Revenue was 10 million in 2025","source_id":"a"},{"claim":"Revenue was 12 million in 2025","source_id":"b"}]
    assert len(heuristic_candidates(c))==1
def test_report_caveat(): assert "does not establish truth" in report_markdown([],[])
