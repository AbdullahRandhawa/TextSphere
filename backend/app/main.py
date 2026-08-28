"""
main.py — FastAPI application entry point.

Start with:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────
    # Import triggers model loading. If any model folder is missing, this
    # raises FileNotFoundError and the server refuses to start.
    from app.tools.registry import TOOL_REGISTRY  # noqa: F401
    logger.info("TextSphere backend ready. Tools loaded: %s", list(TOOL_REGISTRY.keys()))
    yield
    # ── Shutdown (nothing needed) ─────────────────────────────────────────


app = FastAPI(
    title="TextSphere API",
    description="Backend for the TextSphere NLP tool chat app.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import router  # noqa: E402 (after app creation to avoid circular)
app.include_router(router)
