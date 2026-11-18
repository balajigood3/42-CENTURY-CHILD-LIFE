import argparse
from pathlib import Path
from generator.spec import parse_spec
from generator.builder import build_project
p=argparse.ArgumentParser();p.add_argument("--name",required=True);p.add_argument("--entity",default="Record");p.add_argument("--fields",required=True);p.add_argument("--output",default="generated_app")
a=p.parse_args();s=parse_spec(a.name,a.entity,a.fields);root=Path(a.output).resolve();root.mkdir(parents=True,exist_ok=True)
for rel,data in build_project(s).items():
 path=(root/rel).resolve()
 if root not in path.parents: raise ValueError("Unsafe output path")
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data,encoding="utf-8")
print("Generated at",root)
