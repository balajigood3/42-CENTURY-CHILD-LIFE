import pytest
from synthetic_lab.generator import validate_schema, generate_rows, validate_dataset, profile_dataset

SCHEMA = [
    {"name": "age", "type": "integer", "min": 18, "max": 70},
    {"name": "score", "type": "float", "min": 0.0, "max": 100.0},
    {"name": "team", "type": "category", "values": ["A", "B"]},
    {"name": "active", "type": "boolean"}
]

def test_valid_schema():
    assert validate_schema(SCHEMA) is True

def test_reject_empty_schema():
    with pytest.raises(ValueError):
        validate_schema([])

def test_reject_duplicate_columns():
    with pytest.raises(ValueError):
        validate_schema([{"name": "x", "type": "boolean"}, {"name": "x", "type": "boolean"}])

def test_reject_unknown_type():
    with pytest.raises(ValueError):
        validate_schema([{"name": "x", "type": "text"}])

def test_generation_count_and_types():
    rows = generate_rows(SCHEMA, 20)
    assert len(rows) == 20
    assert isinstance(rows[0]["age"], int)
    assert isinstance(rows[0]["score"], float)
    assert rows[0]["team"] in {"A", "B"}
    assert isinstance(rows[0]["active"], bool)

def test_generation_is_reproducible():
    assert generate_rows(SCHEMA, 5, seed=7) == generate_rows(SCHEMA, 5, seed=7)

def test_generation_count_bounds():
    with pytest.raises(ValueError):
        generate_rows(SCHEMA, 0)

def test_valid_dataset_passes():
    rows = generate_rows(SCHEMA, 10)
    assert validate_dataset(rows, SCHEMA)["valid"] is True

def test_invalid_row_detected():
    rows = [{"age": 999, "score": 10.0, "team": "A", "active": True}]
    result = validate_dataset(rows, SCHEMA)
    assert result["valid"] is False
    assert result["issue_count"] >= 1

def test_column_mismatch_detected():
    result = validate_dataset([{"age": 20}], SCHEMA)
    assert any(x["issue"] == "column_mismatch" for x in result["issues"])

def test_profile_numeric_and_categorical():
    rows = generate_rows(SCHEMA, 10)
    profile = profile_dataset(rows, SCHEMA)
    assert "mean" in profile["age"]
    assert "counts" in profile["team"]

def test_profile_rejects_invalid_data():
    with pytest.raises(ValueError):
        profile_dataset([{"age": -1}], SCHEMA)
