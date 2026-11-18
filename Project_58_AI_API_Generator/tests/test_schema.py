import pytest
from api_generator.schema import validate_spec, SpecError

BASE = {"name": "Order", "fields": [{"name": "amount", "type": "float"}]}

def test_valid_spec_defaults():
    result = validate_spec(BASE)
    assert result["endpoint"] == "/orders"
    assert result["methods"] == ["GET", "POST", "PUT", "DELETE"]

@pytest.mark.parametrize("bad", [
    {},
    {"name": "bad-name", "fields": [{"name": "x", "type": "str"}]},
    {"name": "X", "fields": []},
    {"name": "X", "fields": [{"name": "id", "type": "int"}]},
    {"name": "X", "fields": [{"name": "x", "type": "object"}]},
    {"name": "X", "fields": [{"name": "x", "type": "str"}, {"name": "x", "type": "int"}]},
    {"name": "X", "endpoint": "/../admin", "fields": [{"name": "x", "type": "str"}]},
    {"name": "X", "methods": ["TRACE"], "fields": [{"name": "x", "type": "str"}]},
])
def test_invalid_specs_rejected(bad):
    with pytest.raises(SpecError):
        validate_spec(bad)
