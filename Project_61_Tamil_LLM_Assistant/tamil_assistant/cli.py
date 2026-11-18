import argparse
from .core import offline_answer, ollama_answer

def main():
    parser = argparse.ArgumentParser(description="Tamil-first local LLM assistant")
    parser.add_argument("question", nargs="?", help="Question to ask")
    parser.add_argument("--ollama", action="store_true", help="Use local Ollama model")
    parser.add_argument("--model", default="qwen2.5:3b")
    args = parser.parse_args()
    question = args.question or input("உங்கள் கேள்வி: ")
    try:
        answer = ollama_answer(question, args.model) if args.ollama else offline_answer(question)
        print(answer)
    except RuntimeError as exc:
        parser.exit(1, f"பிழை: {exc}\n")

if __name__ == "__main__":
    main()
