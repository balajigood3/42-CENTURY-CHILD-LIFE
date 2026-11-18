import argparse
from pathlib import Path
from .generator import generate_artifacts

def main():
    parser = argparse.ArgumentParser(description="Generate a safe, static DevOps review plan.")
    parser.add_argument("config", help="Path to Docker Compose YAML")
    parser.add_argument("--output", default="generated", help="Artifact output directory")
    args = parser.parse_args()
    config_path = Path(args.config)
    if not config_path.is_file():
        parser.error(f"Configuration file not found: {config_path}")
    report = generate_artifacts(config_path.read_text(encoding="utf-8"), args.output)
    print(f"Analyzed {report['service_count']} service(s); {report['finding_count']} finding(s).")
    print(f"Artifacts written to: {args.output}")

if __name__ == "__main__":
    main()
