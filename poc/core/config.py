import os

# Try loading from local .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Server Configurations
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# AI / Ollama API Config
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "a45e8655957b4c69bc4fa758b8633a52.JfC42-bHH4zqIdhtPwdk6puU")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "https://ollama.com/api/chat")

# Optimized Models for French Conversational Fluidity (Fast, complete, zero truncation)
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5:7b")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "deepseek-v4-flash")

USE_MOCK_AI = False if OLLAMA_API_KEY else True

print(f"[Core Config] Ollama Cloud Integration Active: Key set. Model: {DEFAULT_MODEL}")
