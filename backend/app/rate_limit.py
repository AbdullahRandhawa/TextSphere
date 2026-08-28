"""
rate_limit.py — Per-chat and per-user-per-day rate limiting.

Both limits are enforced server-side before any model/LLM work begins.

Performance note
----------------
check_chat_limit() now accepts the already-fetched chat dict instead of
re-fetching it from Firestore, eliminating a duplicate network round-trip
on every /chat request.
"""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status

from app.config import (
    RATE_LIMIT_CHATS_PER_USER_PER_DAY,
    RATE_LIMIT_MESSAGES_PER_CHAT,
)
from app.firebase import firestore_client as fs


def check_chat_limit(chat: dict) -> None:
    """
    Verify the per-chat message cap has not been reached.
    Accepts the already-fetched chat dict (no extra Firestore read).
    Raises HTTP 429 with a user-friendly message if the cap is exceeded.
    """
    if chat.get("deletedAt") is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat has been deleted.",
        )
    current = chat.get("apiCallCount", 0)
    if current >= RATE_LIMIT_MESSAGES_PER_CHAT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"This chat has reached its {RATE_LIMIT_MESSAGES_PER_CHAT}-message limit. "
                "Start a new chat to continue."
            ),
        )


async def check_daily_chat_limit(uid: str) -> None:
    """
    Verify the per-user-per-day new-chat cap has not been reached.
    Raises HTTP 429 with a user-friendly message (and midnight reset hint).
    """
    today = date.today().isoformat()
    count = await fs.get_daily_chat_count(uid, today)
    if count >= RATE_LIMIT_CHATS_PER_USER_PER_DAY:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"You have created the maximum of {RATE_LIMIT_CHATS_PER_USER_PER_DAY} chats "
                "today. This limit resets at midnight (your local time)."
            ),
        )


async def increment_daily_chat_count(uid: str) -> None:
    today = date.today().isoformat()
    await fs.increment_daily_chat_count(uid, today)
