import argparse, json
from pathlib import Path
from .analyzer import analyze_file, conservative_modernize
from .exporter import export_bundle

def main():
    parser = argparse.ArgumentParser(description="Python legacy-code modernization advisor")
    parser.add_argument("source")
    parser.add_argument("--out", default="modernization_bundle.zip")
    parser.add_argument("--write-copy")
    args = parser.parse_args()
    path = Path(args.source)
    source = path.read_text(encoding="utf-8")
    print(json.dumps(analyze_file(path), indent=2))
    export_bundle(source, args.out, path.name)
    if args.write_copy:
        Path(args.write_copy).write_text(conservative_modernize(source), encoding="utf-8")
    print(f"Exported: {args.out}")

if __name__ == "__main__":
    main()
