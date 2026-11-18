import io
import zipfile
import pytest
from architect.engine import create_architecture, validate_input, bundle_zip, slugify

BRIEF = "Create a booking web platform with user login, appointment reminders and reports."

def test_slug_and_path_safety():
    assert slugify("Clinic Portal!") == "clinic-portal"
    with pytest.raises(ValueError):
        slugify("../unsafe")

def test_validates_brief_and_options():
    with pytest.raises(ValueError):
        validate_input("App", "too short", "small", "internal", "standard")
    with pytest.raises(ValueError):
        validate_input("App", BRIEF, "gigantic", "internal", "standard")

def test_generates_relevant_architecture_files():
    result = create_architecture("Clinic Portal", BRIEF, "medium", "sensitive", "high")
    assert "ARCHITECTURE.md" in result
    assert "appointment" in result["input/project-brief.txt"]
    assert "PostgreSQL" in result["ARCHITECTURE.md"]
    assert "notifications" in result["ARCHITECTURE.md"].lower()
    assert "security-review.md" in result
    assert "Worker" in result["architecture.mmd"]

def test_zip_integrity_and_contents():
    result = create_architecture("Clinic Portal", BRIEF)
    archive = bundle_zip(result)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        assert z.testzip() is None
        assert "ARCHITECTURE.md" in z.namelist()
        assert len(z.namelist()) >= 8

def test_archive_rejects_traversal():
    with pytest.raises(ValueError):
        bundle_zip({"../escape.txt": "bad"})
