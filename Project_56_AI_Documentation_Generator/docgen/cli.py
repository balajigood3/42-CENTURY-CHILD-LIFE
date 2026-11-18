import argparse
from pathlib import Path
from docgen.engine import generate_documentation,make_zip
p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("--name",default="python_project");p.add_argument("--output",default="documentation.zip")
a=p.parse_args();src=Path(a.source)
if src.suffix!=".py" or not src.is_file(): raise SystemExit("Provide an existing .py file")
Path(a.output).write_bytes(make_zip(generate_documentation(src.read_text(encoding="utf-8"),a.name)))
print("Documentation ZIP created:",a.output)
