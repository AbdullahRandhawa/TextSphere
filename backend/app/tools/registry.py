"""
tools/registry.py — pluggable Tool protocol and TOOL_REGISTRY.

Adding a new tool:
  1. Create tools/<name>.py implementing the Tool protocol.
  2. Import it here and add one entry to TOOL_REGISTRY.
  Nothing in the API layer, rate limiter, or frontend needs changing.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """Interface every tool must satisfy."""

    id: str                  # stable key used in API/Firestore, e.g. "sentiment"
    display_name: str        # human-readable label shown in UI
    description: str         # one-liner for the hover tooltip
    base_model: str          # e.g. "DistilBERT"
    fine_tune_dataset: str   # e.g. "SST-2"
    input_schema: dict       # JSON Schema describing required/optional inputs

    def predict(self, **kwargs: Any) -> dict[str, Any]: ...


# ---------------------------------------------------------------------------
# Registry — populated at module import time (tools load their models once)
# ---------------------------------------------------------------------------

def _build_registry() -> dict[str, Tool]:
    # Import here to trigger model loading; failures surface at startup.
    from app.tools.sentiment import SentimentTool
    from app.tools.topic import TopicTool
    from app.tools.ner import NerTool
    from app.tools.summarization import SummarizationTool
    from app.tools.qa import QaTool

    tools: list[Tool] = [
        SentimentTool(),
        TopicTool(),
        NerTool(),
        SummarizationTool(),
        QaTool(),
    ]
    return {t.id: t for t in tools}


TOOL_REGISTRY: dict[str, Tool] = _build_registry()
