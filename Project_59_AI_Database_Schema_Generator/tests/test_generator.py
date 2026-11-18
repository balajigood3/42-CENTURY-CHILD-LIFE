import zipfile
import pytest
from db_schema_gen.generator import generate_sql, generate_mermaid, generate_sqlalchemy, build_artifacts, export_zip
from db_schema_gen.validator import validate_schema, SchemaError

SPEC = {
 "tables": [
  {"name":"users","columns":[{"name":"id","type":"integer","primary_key":True,"nullable":False},{"name":"email","type":"string","unique":True}]},
  {"name":"posts","columns":[{"name":"id","type":"integer","primary_key":True},{"name":"user_id","type":"integer","nullable":False}]}
 ],
 "foreign_keys":[{"table":"posts","column":"user_id","references_table":"users","references_column":"id"}]
}

def test_sql_contains_tables_constraints_and_fk():
    sql = generate_sql(SPEC)
    assert 'CREATE TABLE "users"' in sql
    assert 'UNIQUE' in sql
    assert 'REFERENCES "users" ("id")' in sql

def test_erd_and_orm_are_generated():
    assert "erDiagram" in generate_mermaid(SPEC)
    assert "class users(Base)" in generate_sqlalchemy(SPEC)
    assert "class posts(Base)" in generate_sqlalchemy(SPEC)

def test_reject_unknown_fk_table():
    bad = {"tables":[{"name":"x","columns":[{"name":"id","type":"integer"}]}],
           "foreign_keys":[{"table":"x","column":"id","references_table":"missing","references_column":"id"}]}
    with pytest.raises(SchemaError):
        validate_schema(bad)

def test_reject_duplicate_columns():
    bad = {"tables":[{"name":"x","columns":[{"name":"a","type":"integer"},{"name":"a","type":"string"}]}]}
    with pytest.raises(SchemaError):
        validate_schema(bad)

def test_reject_unsafe_default():
    bad = {"tables":[{"name":"x","columns":[{"name":"name","type":"string","default":"x; DROP TABLE y"}]}]}
    with pytest.raises(ValueError):
        generate_sql(bad)

def test_bundle_zip_integrity(tmp_path):
    out = export_zip(SPEC, tmp_path / "bundle.zip")
    with zipfile.ZipFile(out) as zf:
        assert zf.testzip() is None
        assert {"schema.sql","erd.mmd","models.py","schema.json","Dockerfile","docker-compose.yml"} <= set(zf.namelist())

def test_all_types_supported():
    fields = [{"name":f"c{i}","type":t} for i,t in enumerate(["integer","string","text","boolean","float","datetime","date","uuid"])]
    assert len(validate_schema({"tables":[{"name":"all_types","columns":fields}]})["tables"][0]["columns"]) == 8
