import os
from getpass import getpass

from groq import Groq


# ==========================================================
# 1. GROQ SETUP
# ==========================================================

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API key: ")

MODEL = "openai/gpt-oss-20b"
FALLBACK_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
MODELS_TO_TRY = [MODEL] + FALLBACK_MODELS

client = Groq(api_key=os.environ["GROQ_API_KEY"])

print("Active model:", MODEL)
print("Groq client ready.")


# API base for the news service
BASE_URL = "https://freenewsapi.ai"
