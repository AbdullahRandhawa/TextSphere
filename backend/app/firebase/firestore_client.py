"""
firebase/firestore_client.py — Firestore read/write helpers.

Uses firebase_admin.firestore (wraps google-cloud-firestore).
Async client via firestore.async_client().
Atomic increments done with Firestore server-side Increment transform
(no manual transactions needed).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from firebase_admin import firestore as _fs
from google.cloud.firestore_v1 import AsyncClient
from google.cloud.firestore_v1.field_path import FieldPath

from app.firebase.auth import get_firebase_app

logger = logging.getLogger(__name__)


from firebase_admin import credentials
from app.config import FIREBASE_CREDENTIALS_PATH

_async_db: AsyncClient | None = None


def _db() -> AsyncClient:
    """Return the cached async Firestore client."""
    global _async_db
    if _async_db is None:
        app = get_firebase_app()
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH).get_credential()
        _async_db = AsyncClient(project=app.project_id, credentials=cred)
    return _async_db


# ---------------------------------------------------------------------------
# Chat helpers
# ---------------------------------------------------------------------------

async def get_chat(uid: str, chat_id: str) -> dict | None:
    db = _db()
    doc = await (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .get()
    )
    return doc.to_dict() if doc.exists else None


async def increment_api_call_count(uid: str, chat_id: str) -> None:
    """
    Atomically increments apiCallCount using a server-side transform.
    Fire-and-forget: does NOT read back the new value to avoid an extra
    round-trip that was previously blocking the LLM stream start.
    """
    db = _db()
    ref = (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
    )
    # Single write — no follow-up read needed
    await ref.update({
        "apiCallCount": _fs.Increment(1),
        "updatedAt": datetime.now(timezone.utc),
    })


async def soft_delete_chat(uid: str, chat_id: str) -> None:
    db = _db()
    await (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .update({"deletedAt": datetime.now(timezone.utc)})
    )


async def list_chats(uid: str) -> list[dict]:
    db = _db()
    docs = (
        await db.collection("users")
        .document(uid)
        .collection("chats")
        .where("deletedAt", "==", None)
        .order_by("updatedAt", direction="DESCENDING")
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

async def add_message(
    uid: str,
    chat_id: str,
    role: str,
    text: str,
    tool_used: str | None = None,
    tool_result: dict | None = None,
    created_at: datetime | None = None,
) -> str:
    db = _db()
    now = created_at or datetime.now(timezone.utc)
    ref = (
        db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .collection("messages")
        .document()
    )
    await ref.set({
        "role": role,
        "text": text,
        "toolUsed": tool_used,
        "toolResult": tool_result,
        "createdAt": now,
    })
    return ref.id


async def get_recent_messages(
    uid: str, chat_id: str, limit: int = 5
) -> list[dict[str, Any]]:
    """Return last `limit` messages as {role, content} for the LLM."""
    db = _db()
    docs = (
        await db.collection("users")
        .document(uid)
        .collection("chats")
        .document(chat_id)
        .collection("messages")
        .order_by("createdAt", direction="DESCENDING")
        .limit(limit)
        .get()
    )
    messages = []
    for d in reversed(list(docs)):
        data = d.to_dict()
        messages.append({
            "role": data["role"],
            "content": data.get("text", ""),
        })
    return messages


# ---------------------------------------------------------------------------
# Rate-limit helpers
# ---------------------------------------------------------------------------

async def get_daily_chat_count(uid: str, date_str: str) -> int:
    db = _db()
    doc = await (
        db.collection("users")
        .document(uid)
        .collection("rateLimits")
        .document(date_str)
        .get()
    )
    if not doc.exists:
        return 0
    return doc.to_dict().get("chatsCreated", 0)


async def increment_daily_chat_count(uid: str, date_str: str) -> int:
    """Atomically increments chatsCreated using server-side Increment."""
    db = _db()
    ref = (
        db.collection("users")
        .document(uid)
        .collection("rateLimits")
        .document(date_str)
    )
    await ref.set({"chatsCreated": _fs.Increment(1)}, merge=True)
    snap = await ref.get()
    return (snap.to_dict() or {}).get("chatsCreated", 0)
