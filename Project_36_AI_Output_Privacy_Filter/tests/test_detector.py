import pytest
from privacy_filter.detector import detect, redact, filter_output

def test_email_redaction():
    result = filter_output("Send to alice@example.com")
    assert "[REDACTED_EMAIL]" in result["safe_output"]
    assert result["finding_count"] == 1

def test_pan_detection():
    result = filter_output("PAN ABCDE1234F")
    assert result["findings"][0]["type"] == "india_pan"

def test_aadhaar_detection():
    result = filter_output("ID 1234 5678 9012")
    assert any(x["type"] == "india_aadhaar" for x in result["findings"])

def test_secret_detection():
    result = filter_output("token sk-abcdefghijklmnop")
    assert any(x["type"] == "api_key" for x in result["findings"])
    assert "abcdefghijklmnop" not in result["safe_output"]

def test_block_mode():
    result = filter_output("Email bob@example.com", "block")
    assert result["status"] == "blocked"
    assert result["safe_output"] == ""

def test_report_mode_preserves_text():
    text = "bob@example.com"
    result = filter_output(text, "report")
    assert result["safe_output"] == text
    assert result["status"] == "review_required"

def test_clean_text():
    result = filter_output("The model generated a helpful summary.")
    assert result["status"] == "clean"
    assert result["safe_output"] == "The model generated a helpful summary."

def test_invalid_mode():
    with pytest.raises(ValueError):
        filter_output("hello", "delete")

def test_non_string_rejected():
    with pytest.raises(TypeError):
        filter_output(None)
