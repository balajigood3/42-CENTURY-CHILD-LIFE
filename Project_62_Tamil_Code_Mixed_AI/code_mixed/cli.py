import argparse
from .assistant import answer

def main():
    parser = argparse.ArgumentParser(description="Tamil-English code-mixed assistant")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--ollama", action="store_true")
    parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    question = args.question or input("கேள்வி: ")
    try:
        result = answer(question, use_local=args.ollama, model=args.model)
        print(result["answer"])
        print("Input:", result["script_mix"]["label"])
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"Error: {exc}\n")

if __name__ == "__main__":
    main()
