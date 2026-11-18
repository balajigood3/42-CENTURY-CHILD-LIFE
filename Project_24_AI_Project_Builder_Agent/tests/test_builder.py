import json
import pytest
from app.builder import build_project, slugify, BuilderError

def test_slugify():
    assert slugify("My Demo Project!") == "my_demo_project"

def test_template_build_creates_expected_files(tmp_path):
    result = build_project(
        "Demo Project", "A tiny command line demo",
        output_root=tmp_path, use_llm=False
    )
    root = tmp_path / "demo_project"
    assert (root / "main.py").is_file()
    assert (root / "Dockerfile").is_file()
    assert (root / "docker-compose.yml").is_file()
    manifest = json.loads((root / "project_manifest.json").read_text())
    assert manifest["generator"] == "safe_template_fallback"
    assert result["manifest"]["slug"] == "demo_project"

def test_duplicate_project_name_rejected(tmp_path):
    build_project("Duplicate", "First", output_root=tmp_path, use_llm=False)
    with pytest.raises(BuilderError):
        build_project("Duplicate", "Second", output_root=tmp_path, use_llm=False)

def test_empty_description_rejected(tmp_path):
    with pytest.raises(BuilderError):
        build_project("Empty", "  ", output_root=tmp_path, use_llm=False)
