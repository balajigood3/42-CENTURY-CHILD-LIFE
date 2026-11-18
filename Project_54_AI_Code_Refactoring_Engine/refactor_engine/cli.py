import argparse
from pathlib import Path
from .engine import analyze_and_refactor, make_zip

parser = argparse.ArgumentParser(description="Analyze and safely normalize Python source.")
parser.add_argument("source", help="Path to a .py file")
parser.add_argument("--output", default="refactoring_report.zip")
parser.add_argument("--no-transform", action="store_true")
args = parser.parse_args()
source_path = Path(args.source)
if source_path.suffix != ".py" or not source_path.is_file():
    raise SystemExit("Provide an existing .py source file.")
source = source_path.read_text(encoding="utf-8")
result = analyze_and_refactor(source, apply_safe=not args.no_transform)
Path(args.output).write_bytes(make_zip(result))
print(f"Report written to {args.output}")
