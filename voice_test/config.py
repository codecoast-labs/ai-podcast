import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PROVIDER_KEYS = {
    "openai": "OPENAI_API_KEY",
    "xai": "XAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "hume": "HUME_API_KEY",
}


def get_api_key(provider: str) -> str:
    """Return the API key for a provider, or raise with a clear message."""
    env_var = PROVIDER_KEYS[provider]
    key = os.environ.get(env_var, "").strip()
    if not key:
        raise RuntimeError(
            f"Missing API key: set {env_var} in your .env file or environment."
        )
    return key
