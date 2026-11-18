import io,zipfile,pytest
from generator.spec import parse_spec,slugify
from generator.builder import build_project,make_zip
def test_slug(): assert slugify("Inventory Manager!")=="inventory-manager"
def test_reject_invalid():
 with pytest.raises(ValueError): parse_spec("../escape","Product","name:str")
 with pytest.raises(ValueError): parse_spec("App","Bad-Entity","name:str")
 with pytest.raises(ValueError): parse_spec("App","Product","name:object")
 with pytest.raises(ValueError): parse_spec("App","Product","name:str,name:int")
def test_scaffold():
 f=build_project(parse_spec("Inventory","Product","name:str,qty:int,active:bool"))
 assert "backend/main.py" in f and "frontend/src/App.tsx" in f and "docker-compose.yml" in f
 assert "CREATE TABLE IF NOT EXISTS product" in f["backend/main.py"]
 assert 'method:"POST"' in f["frontend/src/App.tsx"]
def test_zip():
 f=build_project(parse_spec("Inventory","Product","name:str"))
 with zipfile.ZipFile(io.BytesIO(make_zip(f))) as z: assert z.testzip() is None
