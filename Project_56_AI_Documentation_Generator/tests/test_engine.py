import io,zipfile,pytest
from docgen.engine import analyze_source,generate_documentation,make_zip
SRC = "\"\"\"Math module.\"\"\"\nclass Calculator:\n    \"\"\"A calculator.\"\"\"\n    def add(self,a:int,b:int): return a+b\n\ndef multiply(x:float,y:float=1.0):\n    \"\"\"Multiply values.\"\"\"\n    return x*y\nasync def fetch(key:str): return key\n"
def test_ast_inventory():
 a=analyze_source(SRC)
 assert a["module_docstring"]=="Math module."
 assert a["classes"][0]["name"]=="Calculator"
 assert [f["name"] for f in a["functions"]]==["multiply","fetch"]
 assert a["functions"][1]["kind"]=="async"
def test_docs():
 r=generate_documentation(SRC,"Math Tools")
 assert "multiply" in r["API_REFERENCE.md"] and "Calculator" in r["ARCHITECTURE.md"]
 assert r["summary"]["functions"]==2
def test_invalid():
 with pytest.raises(ValueError): analyze_source("def bad(:")
 with pytest.raises(ValueError): generate_documentation("x=1","../bad")
def test_size():
 with pytest.raises(ValueError): analyze_source("x=1\n"*90000)
def test_zip():
 r=generate_documentation(SRC,"Math")
 with zipfile.ZipFile(io.BytesIO(make_zip(r))) as z:
  assert z.testzip() is None
  assert {"README.md","API_REFERENCE.md","ARCHITECTURE.md","analysis.json"} <= set(z.namelist())
