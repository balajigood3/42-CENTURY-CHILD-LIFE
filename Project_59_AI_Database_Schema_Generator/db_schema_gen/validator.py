import re

NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,62}$")
TYPES = {"integer": "INTEGER", "string": "VARCHAR", "text": "TEXT", "boolean": "BOOLEAN",
         "float": "FLOAT", "datetime": "TIMESTAMP", "date": "DATE", "uuid": "UUID"}

class SchemaError(ValueError):
    pass

def validate_schema(data):
    if not isinstance(data, dict):
        raise SchemaError("Schema must be a JSON object.")
    tables = data.get("tables")
    if not isinstance(tables, list) or not tables:
        raise SchemaError("Provide at least one table.")
    table_names, clean_tables = set(), []
    for table in tables:
        if not isinstance(table, dict):
            raise SchemaError("Each table must be an object.")
        name = table.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name):
            raise SchemaError("Table names must be valid SQL identifiers.")
        if name.lower() in table_names:
            raise SchemaError(f"Duplicate table: {name}")
        table_names.add(name.lower())
        columns = table.get("columns")
        if not isinstance(columns, list) or not columns:
            raise SchemaError(f"Table {name} needs at least one column.")
        seen, clean_columns = set(), []
        for col in columns:
            if not isinstance(col, dict):
                raise SchemaError(f"Invalid column in {name}.")
            cname, ctype = col.get("name"), col.get("type")
            if not isinstance(cname, str) or not NAME.fullmatch(cname):
                raise SchemaError(f"Invalid column name in {name}.")
            if cname.lower() in seen:
                raise SchemaError(f"Duplicate column {name}.{cname}")
            seen.add(cname.lower())
            if ctype not in TYPES:
                raise SchemaError(f"Unsupported type for {name}.{cname}.")
            primary = bool(col.get("primary_key", False))
            if primary and col.get("nullable", False):
                raise SchemaError(f"Primary key {name}.{cname} cannot be nullable.")
            clean_columns.append({
                "name": cname, "type": ctype, "primary_key": primary,
                "nullable": bool(col.get("nullable", True)) and not primary,
                "unique": bool(col.get("unique", False)),
                "default": col.get("default")
            })
        clean_tables.append({"name": name, "columns": clean_columns})
    # Validate foreign keys after collecting all table/column definitions.
    clean_fks = []
    for fk in data.get("foreign_keys", []):
        if not isinstance(fk, dict):
            raise SchemaError("Foreign keys must be objects.")
        src_t, src_c = fk.get("table"), fk.get("column")
        dst_t, dst_c = fk.get("references_table"), fk.get("references_column")
        source = next((t for t in clean_tables if t["name"] == src_t), None)
        target = next((t for t in clean_tables if t["name"] == dst_t), None)
        if not source or not target:
            raise SchemaError(f"Foreign key references unknown table: {src_t} -> {dst_t}")
        if src_c not in {c["name"] for c in source["columns"]}:
            raise SchemaError(f"Unknown source column: {src_t}.{src_c}")
        if dst_c not in {c["name"] for c in target["columns"]}:
            raise SchemaError(f"Unknown referenced column: {dst_t}.{dst_c}")
        clean_fks.append({"table": src_t, "column": src_c,
                          "references_table": dst_t, "references_column": dst_c})
    return {"tables": clean_tables, "foreign_keys": clean_fks}
