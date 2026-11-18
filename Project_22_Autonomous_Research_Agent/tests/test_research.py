import pytest
from app.research import validate_url, ResearchError

def test_accepts_http_url():
    assert validate_url("https://example.org/page").startswith("https://")

@pytest.mark.parametrize("url", ["file:///etc/passwd", "javascript:alert(1)", "localhost:8000"])
def test_rejects_non_web_urls(url):
    with pytest.raises(ResearchError):
        validate_url(url)

def test_rejects_localhost():
    with pytest.raises(ResearchError):
        validate_url("http://127.0.0.1:8000/admin")
