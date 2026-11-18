import pytest
from trust_verifier.verifier import normalize_domain, assess_source, assess_claim, assess_text

def test_known_domain_matches():
    source = assess_source({"url":"https://www.nist.gov/publications", "title":"NIST"})
    assert source["domain_status"] == "recognized_domain"

def test_subdomain_match():
    assert normalize_domain("https://www.cisa.gov/") == "cisa.gov"
    assert assess_source({"url":"https://www.blog.nist.gov/x"} )["domain_status"] == "recognized_domain"

def test_lookalike_domain_not_trusted():
    assert assess_source({"url":"https://nist.gov.example.com"})["domain_status"] == "unverified_domain"

def test_missing_source():
    assert assess_source({})["domain_status"] == "no_source"

def test_claim_requires_text():
    with pytest.raises(ValueError):
        assess_claim(" ", [])

def test_claim_flags_absolute_language():
    result = assess_claim("This is 100% accurate and guaranteed.", [])
    assert "absolute_claim" in result["claim_flags"]
    assert result["risk_score"] > 0

def test_known_source_changes_assessment():
    result = assess_claim("A claim", [{"url":"https://www.nist.gov", "title":"NIST"}])
    assert result["assessment"] == "has_recognized_source"

def test_text_type_validation():
    with pytest.raises(TypeError):
        assess_text(None)
