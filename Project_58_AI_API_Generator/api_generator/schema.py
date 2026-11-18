from __future__ import annotations
import re
from typing import Any

IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,49}$")
HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
FIELD_TYPES = {"str": "str", "int": "int", "float": "float", "bool": "bool"}

class SpecError(ValueError):
    pass

def validate_spec(spec: Any) -> dict:
    if not isinstance(spec, dict):
        raise SpecError("API specification must be a JSON object.")
    name = spec.get("name")
    if not isinstance(name, str) or not IDENTIFIER.fullmatch(name):
        raise SpecError("`name` must be an identifier (letters, numbers, underscores; max 50 chars).")
    fields = spec.get("fields")
    if not isinstance(fields, list) or not fields:
        raise SpecError("`fields` must be a non-empty array.")
    seen = set()
    clean_fields = []
    for field in fields:
        if not isinstance(field, dict):
            raise SpecError("Each field must be an object.")
        fname, ftype = field.get("name"), field.get("type")
        if not isinstance(fname, str) or not IDENTIFIER.fullmatch(fname):
            raise SpecError("Every field name must be a valid identifier.")
        if fname in seen or fname == "id":
            raise SpecError(f"Duplicate or reserved field name: {fname}.")
        if ftype not in FIELD_TYPES:
            raise SpecError(f"Unsupported type for {fname}; use one of {', '.join(FIELD_TYPES)}.")
        seen.add(fname)
        clean_fields.append({"name": fname, "type": ftype, "required": bool(field.get("required", True))})
    endpoint = spec.get("endpoint", "/" + name.lower() + "s")
    if not isinstance(endpoint, str) or not endpoint.startswith("/") or "{" in endpoint or "}" in endpoint:
        raise SpecError("`endpoint` must be a static path beginning with /; path parameters are not supported.")
    if len(endpoint) > 100 or ".." in endpoint or "//" in endpoint:
        raise SpecError("Endpoint path is invalid or too long.")
    methods = spec.get("methods", ["GET", "POST", "PUT", "DELETE"])
    if not isinstance(methods, list) or not methods or any(m not in HTTP_METHODS for m in methods):
        raise SpecError(f"`methods` must be a non-empty list using {sorted(HTTP_METHODS)}.")
    methods = list(dict.fromkeys(methods))
    return {"name": name, "endpoint": endpoint, "fields": clean_fields, "methods": methods}
