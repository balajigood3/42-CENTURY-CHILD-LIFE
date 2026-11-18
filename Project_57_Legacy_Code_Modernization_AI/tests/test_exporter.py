import json, zipfile
from legacy_modernizer.exporter import export_bundle

def test_export_bundle(tmp_path):
    nl = chr(10)
    out = tmp_path / "bundle.zip"
    export_bundle(nl.join(["def f():", "    return 1", ""]), out, "sample.py")
    with zipfile.ZipFile(out) as zf:
        assert zf.testzip() is None
        assert set(zf.namelist()) == {"original.py", "modernized.py", "report.json", "REPORT.md"}
        assert json.loads(zf.read("report.json"))["input_file"] == "sample.py"
