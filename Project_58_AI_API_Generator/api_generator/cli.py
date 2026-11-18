import argparse, json
from .generator import export_project

def main():
    parser = argparse.ArgumentParser(description="Generate a FastAPI CRUD starter from JSON specification")
    parser.add_argument("spec", help="Path to JSON API specification")
    parser.add_argument("--out", default="generated_api.zip")
    args = parser.parse_args()
    with open(args.spec, encoding="utf-8") as handle:
        spec = json.load(handle)
    export_project(spec, args.out)
    print(f"Generated project: {args.out}")

if __name__ == "__main__":
    main()
