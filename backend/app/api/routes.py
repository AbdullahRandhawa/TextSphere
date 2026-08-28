"""
api/routes.py — FastAPI route definitions.

Endpoints:
  POST /chat   — SSE stream: optional tool call then streamed LLM commentary
  GET  /tools  — tool registry descriptor list (used by frontend to build UI)
  GET  /health — confirms all tools loaded

Performance notes
-----------------
• The chat document is fetched ONCE in the route handler and passed down to
  check_and_increment_chat_limit() so the rate-limiter never issues a second
  read of the same document.
• increment_api_call_count() and get_recent_messages() are now launched
  concurrently with asyncio.gather() so the context fetch doesn't have to
  wait for the counter write to finish.
• Message persistence saves user FIRST then assistant with explicit timestamps
  so reloading always renders messages in correct order.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.config import CONTEXT_MESSAGE_COUNT
from app.firebase.auth import verify_token
from app.firebase import firestore_client as fs
from app.llm.openrouter_client import stream_commentary
from app.rate_limit import check_chat_limit
from app.schemas import (
    ChatRequest,
    CommentaryChunkEvent,
    DoneEvent,
    ErrorEvent,
    HealthResponse,
    ToolDescriptor,
    ToolResultEvent,
    ToolsResponse,
)
from app.tools.registry import TOOL_REGISTRY

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /tools
# ---------------------------------------------------------------------------

@router.get("/tools", response_model=ToolsResponse)
async def get_tools() -> ToolsResponse:
    """Return all registered tools so the frontend can render dynamically."""
    descriptors = [
        ToolDescriptor(
            id=t.id,
            display_name=t.display_name,
            description=t.description,
            base_model=t.base_model,
            fine_tune_dataset=t.fine_tune_dataset,
            input_schema=t.input_schema,
        )
        for t in TOOL_REGISTRY.values()
    ]
    return ToolsResponse(tools=descriptors)


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Confirm all registered tools are loaded."""
    return HealthResponse(
        status="ok",
        tools_loaded=list(TOOL_REGISTRY.keys()),
    )


# ---------------------------------------------------------------------------
# POST /chat  (SSE)
# ---------------------------------------------------------------------------

def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"



async def _chat_stream(
    uid: str,
    request: ChatRequest,
    chat_doc: dict,
    history: list[dict],
    user_ts: datetime,
) -> AsyncIterator[str]:
    """
    Core generator for the SSE stream.

    Flow:
      1. Rate limit already verified before stream began.
      2. If toolId present → run the tool locally, emit tool_result event.
      3. Stream LLM commentary, emit commentary_chunk events.
      4. Persist messages + increment counter concurrently after stream ends.
      5. Emit done event.
    """
    tool_result_data: dict | None = None
    commentary_text: list[str] = []

    try:
        # -- Tool execution --------------------------------------------------
        if request.toolId:
            tool = TOOL_REGISTRY.get(request.toolId)
            if tool is None:
                yield _sse(ErrorEvent(message=f"Unknown tool: {request.toolId}").model_dump())
                return

            tool_input = request.toolInput or {}
            try:
                raw_result = tool.predict(**tool_input)
            except Exception as exc:
                logger.exception("Tool %s prediction failed", request.toolId)
                yield _sse(ErrorEvent(message=f"Tool error: {exc}").model_dump())
                return

            tool_result_data = {
                "tool_id": tool.id,
                "display_name": tool.display_name,
                "base_model": tool.base_model,
                "fine_tune_dataset": tool.fine_tune_dataset,
                "result": raw_result,
            }
            yield _sse(
                ToolResultEvent(**tool_result_data).model_dump()
            )

        # -- Stream LLM commentary ------------------------------------------
        _t_llm = time.perf_counter()
        _first_chunk = True
        async for chunk in stream_commentary(
            history=history,
            user_message=request.message,
            tool_result=tool_result_data,
        ):
            if _first_chunk:
                logger.info("[TIMING] LLM TTFT=%.0f ms", (time.perf_counter() - _t_llm) * 1000)
                _first_chunk = False
            commentary_text.append(chunk)
            yield _sse(CommentaryChunkEvent(text=chunk).model_dump())

        # -- Persist messages + counter concurrently after stream ends ------
        asst_ts = datetime.now(timezone.utc)
        await fs.add_message(uid, request.chatId, "user", request.message,
                             created_at=user_ts)
        await asyncio.gather(
            fs.add_message(
                uid,
                request.chatId,
                "assistant",
                "".join(commentary_text),
                tool_used=request.toolId,
                tool_result=tool_result_data if tool_result_data else None,
                created_at=asst_ts,
            ),
            fs.increment_api_call_count(uid, request.chatId),
        )

        yield _sse(DoneEvent().model_dump())

    except HTTPException as exc:
        yield _sse(ErrorEvent(message=exc.detail).model_dump())
    except Exception as exc:
        logger.exception("Unexpected error in /chat stream")
        yield _sse(ErrorEvent(message="An unexpected error occurred.").model_dump())


@router.post("/chat")
async def chat(
    request: ChatRequest,
    token_claims: dict = Depends(verify_token),
) -> StreamingResponse:
    t0 = time.perf_counter()
    uid: str = token_claims["uid"]
    logger.info("[TIMING] auth=%.0f ms", (time.perf_counter() - t0) * 1000)

    # Capture user timestamp immediately
    user_ts = datetime.now(timezone.utc)

    # Fetch chat document + recent messages in PARALLEL in a single round-trip
    t_fs = time.perf_counter()
    chat_doc, history = await asyncio.gather(
        fs.get_chat(uid, request.chatId),
        fs.get_recent_messages(uid, request.chatId, limit=CONTEXT_MESSAGE_COUNT),
    )
    logger.info("[TIMING] parallel Firestore fetch=%.0f ms", (time.perf_counter() - t_fs) * 1000)

    if chat_doc is None or chat_doc.get("deletedAt") is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found.",
        )

    # Enforce rate limit
    check_chat_limit(chat_doc)

    logger.info("[TIMING] total pre-stream setup=%.0f ms", (time.perf_counter() - t0) * 1000)
    return StreamingResponse(
        _chat_stream(uid, request, chat_doc, history, user_ts),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
