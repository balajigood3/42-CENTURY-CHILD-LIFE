import argparse
from pathlib import Path
from architect.engine import create_architecture

parser = argparse.ArgumentParser(description="Generate a software architecture pack.")
parser.add_argument("--name", required=True)
parser.add_argument("--brief", required=True)
parser.add_argument("--scale", choices=["small", "medium", "large"], default="small")
parser.add_argument("--sensitivity", choices=["public", "internal", "sensitive"], default="internal")
parser.add_argument("--availability", choices=["standard", "high"], default="standard")
parser.add_argument("--output", default="architecture_output")
args = parser.parse_args()
files = create_architecture(args.name, args.brief, args.scale, args.sensitivity, args.availability)
root = Path(args.output).resolve()
root.mkdir(parents=True, exist_ok=True)
for relative, content in files.items():
    target = (root / relative).resolve()
    if root not in target.parents:
        raise ValueError("Unsafe output path.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
print(f"Generated {len(files)} files at {root}")
