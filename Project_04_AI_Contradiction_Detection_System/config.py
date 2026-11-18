import os
OLLAMA_URL=os.getenv("OLLAMA_URL","http://localhost:11434/api/generate")
MODEL_NAME=os.getenv("MODEL_NAME","qwen2.5:3b")
REQUEST_TIMEOUT=int(os.getenv("REQUEST_TIMEOUT","180"))
MAX_INPUT_CHARS=int(os.getenv("MAX_INPUT_CHARS","12000"))
