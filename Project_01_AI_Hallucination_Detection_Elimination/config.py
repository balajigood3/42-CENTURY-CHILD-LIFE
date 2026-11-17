import os
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
TOP_K = int(os.getenv("TOP_K", "4"))
