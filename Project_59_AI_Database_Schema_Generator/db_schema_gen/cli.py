import argparse, json
from .generator import export_zip

def main():
    parser = argparse.ArgumentParser(description="Generate SQL, ERD and SQLAlchemy models from a schema JSON file.")
    parser.add_argument("spec")
    parser.add_argument("--out", default="database_schema_bundle.zip")
    args = parser.parse_args()
    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    export_zip(spec, args.out)
    print(f"Created {args.out}")

if __name__ == "__main__":
    main()
