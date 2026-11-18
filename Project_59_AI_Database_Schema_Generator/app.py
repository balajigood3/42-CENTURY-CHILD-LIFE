import json, tempfile, os
import streamlit as st
from db_schema_gen.generator import build_artifacts, export_zip
from db_schema_gen.validator import SchemaError

st.set_page_config(page_title="AI Database Schema Generator", layout="wide")
st.title("AI Database Schema Generator")
st.caption("Generate SQL DDL, ER diagrams and SQLAlchemy models from a structured schema. No paid API keys.")
sample = {
  "tables": [
    {"name": "customers", "columns": [
      {"name": "id", "type": "integer", "primary_key": True, "nullable": False},
      {"name": "name", "type": "string", "nullable": False},
      {"name": "email", "type": "string", "unique": True}
    ]},
    {"name": "orders", "columns": [
      {"name": "id", "type": "integer", "primary_key": True, "nullable": False},
      {"name": "customer_id", "type": "integer", "nullable": False},
      {"name": "total", "type": "float", "nullable": False}
    ]}
  ],
  "foreign_keys": [{"table": "orders", "column": "customer_id", "references_table": "customers", "references_column": "id"}]
}
raw = st.text_area("Database schema specification (JSON)", json.dumps(sample, indent=2), height=360)
if st.button("Validate and generate schema", type="primary"):
    try:
        spec = json.loads(raw)
        artifacts = build_artifacts(spec)
        st.success(f"Generated {len(artifacts)} artifacts.")
        choice = st.selectbox("Preview artifact", list(artifacts))
        st.code(artifacts[choice], language="sql" if choice.endswith(".sql") else "python" if choice.endswith(".py") else "text")
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        export_zip(spec, tmp_path)
        with open(tmp_path, "rb") as f:
            st.download_button("Download schema bundle", f.read(), file_name="database_schema_bundle.zip")
        os.unlink(tmp_path)
    except (json.JSONDecodeError, SchemaError, ValueError) as exc:
        st.error(str(exc))
st.warning("Generated DDL is a starting point. Review types, constraints, indexes, migrations and database-specific behavior before applying it.")
