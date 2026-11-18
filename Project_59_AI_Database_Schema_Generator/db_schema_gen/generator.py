import json
from pathlib import Path
from .validator import validate_schema, TYPES

def _sql_default(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str) and len(value) <= 100 and not any(x in value for x in (";", "--", "/*", "*/")):
        return "'" + value.replace("'", "''") + "'"
    raise ValueError("Default must be a short safe scalar value.")

def generate_sql(raw):
    schema = validate_schema(raw)
    statements = []
    for table in schema["tables"]:
        pieces = []
        for col in table["columns"]:
            line = f'"{col["name"]}" {TYPES[col["type"]]}'
            if col["primary_key"]:
                line += " PRIMARY KEY"
            if not col["nullable"]:
                line += " NOT NULL"
            if col["unique"]:
                line += " UNIQUE"
            default = _sql_default(col["default"])
            if default is not None:
                line += f" DEFAULT {default}"
            pieces.append(line)
        for fk in schema["foreign_keys"]:
            if fk["table"] == table["name"]:
                pieces.append(f'FOREIGN KEY ("{fk["column"]}") REFERENCES "{fk["references_table"]}" ("{fk["references_column"]}")')
        statements.append(f'CREATE TABLE "{table["name"]}" (\n    ' + ",\n    ".join(pieces) + "\n);")
    return "\n\n".join(statements) + "\n"

def generate_mermaid(raw):
    schema = validate_schema(raw)
    lines = ["erDiagram"]
    for table in schema["tables"]:
        lines.append(f'    {table["name"]} {{')
        for col in table["columns"]:
            key = " PK" if col["primary_key"] else ""
            lines.append(f'        {col["type"]} {col["name"]}{key}')
        lines.append("    }")
    for fk in schema["foreign_keys"]:
        lines.append(f'    {fk["references_table"]} ||--o{{ {fk["table"]} : references')
    return "\n".join(lines) + "\n"

def generate_sqlalchemy(raw):
    schema = validate_schema(raw)
    lines = ["from sqlalchemy.orm import DeclarativeBase, mapped_column", "from sqlalchemy import Integer, String, Text, Boolean, Float, DateTime, Date, Uuid", "", "class Base(DeclarativeBase):", "    pass", ""]
    types = {"integer": "Integer", "string": "String(255)", "text": "Text", "boolean": "Boolean", "float": "Float", "datetime": "DateTime", "date": "Date", "uuid": "Uuid"}
    for table in schema["tables"]:
        lines.append(f"class {table['name']}(Base):")
        lines.append(f'    __tablename__ = "{table["name"]}"')
        for col in table["columns"]:
            args = [types[col["type"]]]
            if col["primary_key"]:
                args.append("primary_key=True")
            if not col["nullable"]:
                args.append("nullable=False")
            if col["unique"]:
                args.append("unique=True")
            lines.append(f'    {col["name"]} = mapped_column({", ".join(args)})')
        lines.append("")
    return "\n".join(lines)

def build_artifacts(raw):
    schema = validate_schema(raw)
    return {
        "schema.json": json.dumps(schema, indent=2) + "\n",
        "schema.sql": generate_sql(schema),
        "erd.mmd": generate_mermaid(schema),
        "models.py": generate_sqlalchemy(schema),
        "README.md": """# Generated Database Schema

Review the generated DDL and ORM models before applying them. Back up databases and test migrations in a non-production environment first.
""",
        "requirements.txt": "sqlalchemy>=2.0,<3.0\n",
        "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-c", "print('Schema artifacts are ready')"]
""",
        "docker-compose.yml": """services:
  schema-generator-artifacts:
    build: .
    command: ["python", "-c", "print('Schema artifacts are ready')"]
""",
        ".dockerignore": "__pycache__/\n.venv/\n.pytest_cache/\n.git/\n"
    }

def export_zip(raw, output):
    import zipfile
    artifacts = build_artifacts(raw)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in artifacts.items():
            zf.writestr(name, content)
    return output
