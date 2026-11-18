import json
import pytest
from meeting_intelligence.analyzer import analyze_transcript, validate_analysis
from meeting_intelligence.exporter import export_json, export_markdown

TRANSCRIPT = """The team reviewed the launch schedule.
Priya will prepare the API test report by Friday.
We decided to freeze the release scope for this sprint.
Risk: vendor access may delay testing.
Arun needs to update the deployment checklist.
The team agreed that QA sign-off is required before release."""

def test_extracts_action_items():
    result = analyze_transcript(TRANSCRIPT)
    owners = [item["owner"] for item in result["action_items"]]
    assert "Priya" in owners

def test_extracts_decisions():
    result = analyze_transcript(TRANSCRIPT)
    assert any("decided" in item.lower() for item in result["decisions"])

def test_extracts_risks():
    result = analyze_transcript(TRANSCRIPT)
    assert any("vendor access" in item.lower() for item in result["risks_and_blockers"])

def test_extracts_topics():
    result = analyze_transcript(TRANSCRIPT)
    assert result["key_topics"]

def test_short_transcript_rejected():
    with pytest.raises(ValueError):
        analyze_transcript("Too short")

def test_oversized_transcript_rejected():
    with pytest.raises(ValueError):
        analyze_transcript("x" * 150001)

def test_empty_title_fallback():
    assert analyze_transcript(TRANSCRIPT, " ")["meeting_title"] == "Meeting"

def test_validation_accepts_generated_result():
    assert validate_analysis(analyze_transcript(TRANSCRIPT))["action_items"]

def test_validation_rejects_missing_fields():
    with pytest.raises(ValueError):
        validate_analysis({"meeting_title": "Only title"})

def test_json_export(tmp_path):
    target = tmp_path / "meeting.json"
    export_json(analyze_transcript(TRANSCRIPT), target)
    assert json.loads(target.read_text())["meeting_title"] == "Meeting"

def test_markdown_export(tmp_path):
    target = tmp_path / "meeting.md"
    export_markdown(analyze_transcript(TRANSCRIPT), target)
    assert "Action items" in target.read_text()

def test_duplicate_action_deduplication():
    text = TRANSCRIPT + "\nPriya will prepare the API test report by Friday."
    result = analyze_transcript(text)
    assert len([x for x in result["action_items"] if x["owner"] == "Priya"]) == 1
