from leak_guard.scanner import scan_text, _luhn_valid

def test_email_detection_and_masking():
    report = scan_text("Contact alice@example.com for details.")
    assert report.finding_count == 1
    assert "[REDACTED_EMAIL]" in report.sanitized_text
    assert "alice@example.com" not in report.sanitized_text

def test_api_secret_detection():
    report = scan_text("API_KEY=abcdef1234567890")
    assert any(x["category"] == "api_key_assignment" for x in report.findings)
    assert "[REDACTED_SECRET]" in report.sanitized_text
    assert report.risk_level == "High"

def test_pan_like_detection():
    report = scan_text("PAN: ABCDE1234F")
    assert any(x["category"] == "pan_like" for x in report.findings)
    assert "[REDACTED_GOV_ID]" in report.sanitized_text

def test_aadhaar_like_detection():
    report = scan_text("ID 1234 5678 9012")
    assert any(x["category"] == "aadhaar_like" for x in report.findings)

def test_luhn_valid_card_like_number():
    assert _luhn_valid("4111 1111 1111 1111")
    report = scan_text("Card 4111 1111 1111 1111")
    assert any(x["category"] == "credit_card_like" for x in report.findings)
    assert "[REDACTED_PAYMENT_CARD]" in report.sanitized_text

def test_invalid_card_number_not_flagged():
    report = scan_text("Reference 4111 1111 1111 1112")
    assert not any(x["category"] == "credit_card_like" for x in report.findings)

def test_private_key_header_detection():
    report = scan_text("-----BEGIN PRIVATE KEY-----")
    assert any(x["category"] == "private_key_header" for x in report.findings)

def test_clean_text():
    report = scan_text("The quarterly report is ready for review.")
    assert report.finding_count == 0
    assert report.risk_score == 0
    assert report.risk_level == "None detected"

def test_multiple_sensitive_types():
    report = scan_text("Mail bob@example.org and token=secret-value-12345")
    assert report.finding_count >= 2
    assert report.risk_score >= 60
