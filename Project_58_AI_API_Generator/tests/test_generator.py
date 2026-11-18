import zipfile
from api_generator.generator import generate_files, export_project

SPEC = {"name": "Task", "endpoint": "/tasks",
        "fields": [{"name": "title", "type": "str"}, {"name": "done", "type": "bool", "required": False}],
        "methods": ["GET", "POST", "PATCH", "DELETE"]}

def test_generates_expected_files_and_routes():
    files = generate_files(SPEC)
    assert {"main.py", "models.py", "requirements.txt", "Dockerfile", "docker-compose.yml"} <= set(files)
    assert "@app.post" in files["main.py"]
    assert "@app.patch" in files["main.py"]
    assert "title: str" in files["models.py"]

def test_export_zip_is_valid(tmp_path):
    output = export_project(SPEC, tmp_path / "api.zip")
    with zipfile.ZipFile(output) as zf:
        assert zf.testzip() is None
        assert "main.py" in zf.namelist()
        assert "docker-compose.yml" in zf.namelist()

def test_methods_are_respected():
    files = generate_files({"name": "Note", "fields": [{"name": "body", "type": "str"}], "methods": ["GET"]})
    assert "@app.get" in files["main.py"]
    assert "@app.post" not in files["main.py"]
