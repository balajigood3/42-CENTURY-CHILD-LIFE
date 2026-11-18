"""Generate and validate synthetic tabular data from a user-provided schema."""
from __future__ import annotations
import math
import random
from collections import Counter

SUPPORTED = {"integer", "float", "category", "boolean"}

def validate_schema(schema):
    if not isinstance(schema, list) or not schema:
        raise ValueError("Schema must be a non-empty list.")
    names = set()
    for col in schema:
        if not isinstance(col, dict):
            raise ValueError("Each schema column must be an object.")
        name, kind = col.get("name"), col.get("type")
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("Column names must be non-empty and unique.")
        if kind not in SUPPORTED:
            raise ValueError(f"Unsupported type for {name}; choose {', '.join(sorted(SUPPORTED))}.")
        names.add(name)
        if kind in {"integer", "float"}:
            lo, hi = col.get("min"), col.get("max")
            if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)) or not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
                raise ValueError(f"{name} requires finite min and max with min <= max.")
        if kind == "category":
            values = col.get("values")
            if not isinstance(values, list) or not values:
                raise ValueError(f"{name} requires a non-empty values list.")
    return True

def generate_rows(schema, count, seed=42):
    validate_schema(schema)
    if not isinstance(count, int) or not 1 <= count <= 100000:
        raise ValueError("count must be between 1 and 100000.")
    rng = random.Random(seed)
    rows = []
    for _ in range(count):
        row = {}
        for col in schema:
            name, kind = col["name"], col["type"]
            if kind == "integer":
                row[name] = rng.randint(int(col["min"]), int(col["max"]))
            elif kind == "float":
                row[name] = round(rng.uniform(float(col["min"]), float(col["max"])), 4)
            elif kind == "category":
                row[name] = rng.choice(col["values"])
            elif kind == "boolean":
                row[name] = rng.choice([True, False])
        rows.append(row)
    return rows

def validate_dataset(rows, schema):
    validate_schema(schema)
    if not isinstance(rows, list) or not rows:
        raise ValueError("Dataset must contain at least one row.")
    issues = []
    expected = {col["name"] for col in schema}
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            issues.append({"row": idx, "issue": "row_not_object"})
            continue
        if set(row) != expected:
            issues.append({"row": idx, "issue": "column_mismatch",
                           "missing": sorted(expected - set(row)),
                           "extra": sorted(set(row) - expected)})
        for col in schema:
            name, kind = col["name"], col["type"]
            value = row.get(name)
            valid = True
            if kind == "integer":
                valid = isinstance(value, int) and not isinstance(value, bool) and col["min"] <= value <= col["max"]
            elif kind == "float":
                valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and col["min"] <= value <= col["max"]
            elif kind == "category":
                valid = value in col["values"]
            elif kind == "boolean":
                valid = isinstance(value, bool)
            if not valid:
                issues.append({"row": idx, "column": name, "issue": "invalid_value", "value": repr(value)})
    return {"valid": len(issues) == 0, "row_count": len(rows),
            "issue_count": len(issues), "issues": issues[:500]}

def profile_dataset(rows, schema):
    validation = validate_dataset(rows, schema)
    if not validation["valid"]:
        raise ValueError("Cannot profile an invalid dataset; fix validation issues first.")
    profile = {}
    for col in schema:
        name, kind = col["name"], col["type"]
        values = [r[name] for r in rows]
        if kind in {"integer", "float"}:
            nums = [float(x) for x in values]
            profile[name] = {"type": kind, "min": min(nums), "max": max(nums),
                             "mean": sum(nums) / len(nums)}
        else:
            profile[name] = {"type": kind, "counts": dict(Counter(map(str, values)))}
    return profile
