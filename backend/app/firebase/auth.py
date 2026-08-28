"""
firebase/auth.py — Firebase ID token verification.

Provides:
  • get_firebase_app()  — lazily initialise firebase_admin SDK once
  • verify_token()      — FastAPI dependency that extracts and verifies the
                          Bearer token from the Authorization header,
                          returning the decoded claims dict.
"""

from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import FIREBASE_CREDENTIALS_PATH

logger = logging.getLogger(__name__)

_bearer_scheme = HTTPBearer(auto_error=True)


@lru_cache(maxsize=1)
def get_firebase_app() -> firebase_admin.App:
    """Return (or create) the default firebase_admin App."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        return firebase_admin.initialize_app(cred)


async def verify_token(
    creds: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency.
    Raises HTTP 401 if the token is missing, invalid, or expired.
    Returns the decoded token claims (includes uid, email, etc.).

    NOTE: verify_id_token() is synchronous and makes a network call to fetch
    Google's public keys on first use (cached ~1 h after that). Running it
    in a thread pool executor prevents it from blocking the asyncio event loop,
    which was the primary source of pre-LLM latency (3-8 s per request).
    """
    get_firebase_app()  # ensure SDK is initialised
    try:
        loop = asyncio.get_event_loop()
        decoded = await loop.run_in_executor(
            None, auth.verify_id_token, creds.credentials
        )
        return decoded
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired. Please sign in again.",
        )
    except auth.InvalidIdTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID token: {exc}",
        )
    except Exception as exc:
        logger.exception("Token verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not verify token: {exc}",
        )
