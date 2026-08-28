"""
config.py — centralised configuration for TextSphere backend.

All secrets / paths come from environment variables or sensible
defaults so that nothing sensitive is ever committed to source control.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_BACKEND_DIR  = Path(__file__).resolve().parent.parent   # backend/
_APP_DIR      = Path(__file__).resolve().parent          # backend/app/

# All fine-tuned model weights live under backend/app/finetuned_models/
# Each sub-folder is an NTFS junction pointing to the original model directory.
FINETUNED_MODELS_DIR = _APP_DIR / "finetuned_models"

# Mapping: tool id → absolute path to the fine-tuned model folder
MODEL_PATHS: dict[str, Path] = {
    "sentiment":     FINETUNED_MODELS_DIR / "sentiment",
    "topic":         FINETUNED_MODELS_DIR / "topic",
    "ner":           FINETUNED_MODELS_DIR / "ner",
    "summarization": FINETUNED_MODELS_DIR / "summarization",
    "qa":            FINETUNED_MODELS_DIR / "qa",
}

# ---------------------------------------------------------------------------
# Firebase (server-side)
# ---------------------------------------------------------------------------

FIREBASE_CREDENTIALS_PATH: str = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    str(_BACKEND_DIR / "firebase_credentials.json"),
)

# ---------------------------------------------------------------------------
# OpenRouter / LLM
# ---------------------------------------------------------------------------

OPENROUTER_API_KEY: str  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL: str    = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

# ---------------------------------------------------------------------------
# Rate limits (enforced server-side)
# ---------------------------------------------------------------------------

RATE_LIMIT_MESSAGES_PER_CHAT: int = int(
    os.getenv("RATE_LIMIT_MESSAGES_PER_CHAT", "50")
)
RATE_LIMIT_CHATS_PER_USER_PER_DAY: int = int(
    os.getenv("RATE_LIMIT_CHATS_PER_USER_PER_DAY", "20")
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

# ---------------------------------------------------------------------------
# LLM context window
# ---------------------------------------------------------------------------

CONTEXT_MESSAGE_COUNT: int = 5
