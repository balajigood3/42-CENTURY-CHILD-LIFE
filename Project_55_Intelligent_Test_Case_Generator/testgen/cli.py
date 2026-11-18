
import argparse
from pathlib import Path
from .engine import generate_tests, make_zip
parser = argparse.ArgumentParser(description="Generate pytest test skeletons from Python source.")
parser.add_argument("source")
parser.add_argument("--output", default="generated_tests.zip")
parser.add_argument("--no-edge-cases", action="store_true")
args = parser.parse_args()
path = Path(args.source)
if path.suffix != ".py" or not path.is_file():
    raise SystemExit("Provide an existing .py file.")
result = generate_tests(path.read_text(encoding="utf-8"), not args.no_edge_cases)
Path(args.output).write_bytes(make_zip(result))
print(f"Generated {len(result['cases'])} test cases in {args.output}")
