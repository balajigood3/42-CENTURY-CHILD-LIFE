import json
import pytest
from product_design.generator import generate_product_concept, infer_domain, validate_concept
from product_design.exporter import export_json, export_markdown

def test_domain_detection_education():
    assert infer_domain("Students need online courses and learning progress") == "education"

def test_domain_detection_marketplace():
    assert infer_domain("Build an ecommerce marketplace for sellers") == "marketplace"

def test_generate_concept_structure():
    result = generate_product_concept(
        "LearnPath", "Students need a learning platform for courses and practice.",
        "College students"
    )
    assert result["domain"] == "education"
    assert len(result["feature_backlog"]) >= 3

def test_empty_name_rejected():
    with pytest.raises(ValueError):
        generate_product_concept(" ", "A useful problem statement for testing.", "Users")

def test_short_problem_rejected():
    with pytest.raises(ValueError):
        generate_product_concept("App", "tiny", "Users")

def test_missing_audience_rejected():
    with pytest.raises(ValueError):
        generate_product_concept("App", "A sufficiently long problem statement.", " ")

def test_long_problem_rejected():
    with pytest.raises(ValueError):
        generate_product_concept("App", "x" * 1501, "Users")

def test_mvp_can_be_disabled():
    result = generate_product_concept("App", "A useful project management tool for teams.",
                                       "Project teams", include_mvp=False)
    assert result["mvp_scope"] == []

def test_feature_ids_unique():
    result = generate_product_concept("App", "A useful shopping marketplace for buyers.",
                                       "Online shoppers")
    ids = [x["feature_id"] for x in result["feature_backlog"]]
    assert len(ids) == len(set(ids))

def test_validation_accepts_generated_concept():
    result = generate_product_concept("App", "A useful project management tool for teams.",
                                       "Project teams")
    assert validate_concept(result)["product_name"] == "App"

def test_validation_rejects_missing_fields():
    with pytest.raises(ValueError):
        validate_concept({"product_name": "Only name"})

def test_json_export(tmp_path):
    result = generate_product_concept("App", "A useful project management tool for teams.", "Teams")
    path = tmp_path / "concept.json"
    export_json(result, path)
    assert json.loads(path.read_text())["product_name"] == "App"

def test_markdown_export(tmp_path):
    result = generate_product_concept("App", "A useful project management tool for teams.", "Teams")
    path = tmp_path / "concept.md"
    export_markdown(result, path)
    assert "Feature backlog" in path.read_text()
