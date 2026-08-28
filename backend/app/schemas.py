"""
schemas.py — Pydantic models for request/response validation.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# /chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    chatId: str = Field(..., description="Firestore chat document ID")
    message: str = Field(..., min_length=1, max_length=8000)
    toolId: Optional[str] = Field(None, description="Tool id from TOOL_REGISTRY")
    toolInput: Optional[dict[str, Any]] = Field(
        None, description="Validated inputs for the selected tool"
    )


# ---------------------------------------------------------------------------
# /tools
# ---------------------------------------------------------------------------

class ToolDescriptor(BaseModel):
    id: str
    display_name: str
    description: str
    base_model: str
    fine_tune_dataset: str
    input_schema: dict[str, Any]


class ToolsResponse(BaseModel):
    tools: list[ToolDescriptor]


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    tools_loaded: list[str]


# ---------------------------------------------------------------------------
# SSE event envelopes (serialised to JSON inside SSE data field)
# ---------------------------------------------------------------------------

class ToolResultEvent(BaseModel):
    type: str = "tool_result"
    tool_id: str
    display_name: str
    base_model: str
    fine_tune_dataset: str
    result: dict[str, Any]


class CommentaryChunkEvent(BaseModel):
    type: str = "commentary_chunk"
    text: str


class DoneEvent(BaseModel):
    type: str = "done"


class ErrorEvent(BaseModel):
    type: str = "error"
    message: str
