// hooks/useStreamingChat.js
// Consumes the SSE stream from POST /chat.
// Handles: tool_result event → tool bubble, commentary_chunk → streaming text,
// done → finalize, error → surface message.

import { useState, useRef, useCallback } from 'react';
import { auth } from '../firebase';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function useStreamingChat() {
  const [messages, setMessages] = useState([]);   // rendered turn list
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef(null);

  // Add a completed turn (user message + assistant turn) to state
  const _appendTurn = (userMsg, toolResult, commentary, toolId) => {
    setMessages((prev) => [
      ...prev,
      { id: Date.now() + '-user', role: 'user', text: userMsg },
      { id: Date.now() + '-assistant', role: 'assistant', toolResult, commentary, toolId },
    ]);
  };

  const sendMessage = useCallback(async ({
    chatId,
    message,
    toolId,
    toolInput,
    onToolResult,
    onCommentaryChunk,
    onDone,
    onError,
  }) => {
    if (streaming) return;

    const token = await auth.currentUser?.getIdToken();
    if (!token) { onError?.('Not authenticated'); return; }

    setStreaming(true);
    abortRef.current = new AbortController();

    let toolResultData = null;
    let commentaryBuffer = '';

    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ chatId, message, toolId: toolId || undefined, toolInput: toolInput || undefined }),
        signal: abortRef.current.signal,
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ detail: resp.statusText }));
        onError?.(err.detail || 'Request failed');
        return;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop(); // keep incomplete line

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const raw = line.slice(6).trim();
          if (!raw) continue;

          let event;
          try { event = JSON.parse(raw); } catch { continue; }

          if (event.type === 'tool_result') {
            toolResultData = event;
            onToolResult?.(event);
          } else if (event.type === 'commentary_chunk') {
            commentaryBuffer += event.text;
            onCommentaryChunk?.(event.text);
          } else if (event.type === 'done') {
            onDone?.();
            break;
          } else if (event.type === 'error') {
            onError?.(event.message);
            break;
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        onError?.(err.message || 'Connection error');
      }
    } finally {
      setStreaming(false);
    }
  }, [streaming]);

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setStreaming(false);
  }, []);

  return { messages, setMessages, streaming, sendMessage, abort };
}
