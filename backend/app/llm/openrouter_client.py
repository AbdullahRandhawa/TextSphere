"""
llm/openrouter_client.py — OpenRouter chat + SSE streaming.

The model is configurable via the OPENROUTER_MODEL env var so it can be
swapped without touching any other code.

Performance note
----------------
A single shared httpx.AsyncClient is kept alive for the process lifetime.
This reuses the existing TCP+TLS connection to openrouter.ai (HTTP/2
multiplexing or HTTP/1.1 keep-alive), avoiding a fresh TLS handshake on
every chat message which was a significant source of first-token latency.
"""

from __future__ import annotations

import json
import logging
from typing import AsyncIterator

import httpx

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are TextSphere's friendly AI assistant. You can hold a normal conversation AND help users get the most out of five specialised NLP models built into the app.

== THE FIVE NLP TOOLS ==
• Sentiment Analyzer  — classifies text as Positive or Negative (fine-tuned BERT)
• Topic Classifier    — labels text as World, Sports, Business, or Sci/Tech (fine-tuned BERT)
• Named Entity Recognizer — extracts people, organisations, locations (fine-tuned BERT, CoNLL-2003)
• Text Summarizer     — condenses long passages into a short summary (fine-tuned T5)
• Question Answering  — answers a question FROM a passage the user supplies (fine-tuned DistilBERT, SQuAD)
  ↳ IMPORTANT: The Q/A tool is *extractive* — it reads a context paragraph the user provides and pulls
    the answer out of it. It CANNOT look things up from the internet or from its own knowledge.
    NEVER recommend Q/A when the user is asking a general knowledge question and has no document to provide.

== HOW TO BEHAVE ==

1. CHITCHAT & GENERAL QUESTIONS — just answer naturally, like a helpful friend.
   Do NOT refuse to engage or demand the user pick a tool. If a tool is loosely
   relevant, you may mention it briefly at the very end as a tip — never as a gate.

2. TOOL RESULTS — when a tool was used this turn you'll receive its structured output.
   Explain the result in plain, friendly language. Surface key insights, add caveats
   where useful. Never repeat the raw JSON verbatim.

3. TOOL SUGGESTIONS — only suggest a tool when it is genuinely the right fit:
   - Sentiment: user has text and wants to know its sentiment/tone.
   - Topic: user has text and wants to know its news category.
   - NER: user has text and wants entities (people/orgs/places) extracted.
   - Summarizer: user has a long passage and wants a shorter version.
   - Q/A: user has a passage AND a specific question about that passage.
   When you do suggest, phrase it as a soft tip, e.g.
   "By the way, you could also try the Sentiment Analyzer on that text."

4. NEVER refuse to answer a factual or conversational question by saying "use a tool instead."
   Always give a real answer first. Tools are a bonus, not a replacement for you.

5. Keep answers concise but genuinely helpful. Use Markdown where it aids clarity.
   Never claim to run the models yourself — attribute results to the fine-tuned model.
"""

# ---------------------------------------------------------------------------
# Persistent HTTP client — reused across all requests
# ---------------------------------------------------------------------------

_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    """
    Return the shared httpx.AsyncClient, creating it on first call.

    Limits:
      • keepalive_expiry=30s  — drops idle connections quickly to avoid
        getting surprised by server-side RST after long idle periods.
      • max_connections=20    — enough headroom for concurrent requests.
      • timeout=60s           — matches previous per-request timeout.
    """
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            http2=True,                          # enables HTTP/2 multiplexing
            timeout=httpx.Timeout(60.0),
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
                keepalive_expiry=30,
            ),
        )
    return _http_client


# ---------------------------------------------------------------------------
# Message builder
# ---------------------------------------------------------------------------

def _build_messages(
    history: list[dict],
    user_message: str,
    tool_result: dict | None = None,
) -> list[dict]:
    """
    Construct the messages array for the OpenRouter API call.

    history  — last N {role, content} dicts from Firestore.
    user_message — the current user turn's text.
    tool_result  — if a tool was used, the structured result dict plus metadata.
    """
    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend(history)

    if tool_result:
        # The user's message becomes context for the commentary; the tool
        # output is injected as a system note so the LLM can explain it.
        tool_context = (
            f"[Tool used: {tool_result['display_name']} "
            f"({tool_result['base_model']}, fine-tuned on "
            f"{tool_result['fine_tune_dataset']}]\n"
            f"Raw tool output: {json.dumps(tool_result['result'], ensure_ascii=False)}\n\n"
            f"User message: {user_message}"
        )
        messages.append({"role": "user", "content": tool_context})
    else:
        messages.append({"role": "user", "content": user_message})

    return messages


# ---------------------------------------------------------------------------
# Streaming commentary
# ---------------------------------------------------------------------------

async def stream_commentary(
    history: list[dict],
    user_message: str,
    tool_result: dict | None = None,
) -> AsyncIterator[str]:
    """
    Yield text chunks from the OpenRouter streaming chat completion.
    Each yielded value is a raw text chunk (not a full SSE envelope).

    Uses the shared persistent HTTP client to avoid per-request TLS overhead.
    """
    if not OPENROUTER_API_KEY:
        yield "[OpenRouter API key not configured — set OPENROUTER_API_KEY in .env]"
        return

    messages = _build_messages(history, user_message, tool_result)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://textsphere.app",
        "X-Title": "TextSphere",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "stream": True,
        "max_tokens": 600,   # cap output — biggest lever for reducing TTFT on DeepSeek
        "temperature": 0.7,
    }

    client = _get_http_client()
    async with client.stream(
        "POST",
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
    ) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            if not line.startswith("data: "):
                continue
            data = line[len("data: "):]
            if data.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta
            except (json.JSONDecodeError, KeyError, IndexError):
                continue
