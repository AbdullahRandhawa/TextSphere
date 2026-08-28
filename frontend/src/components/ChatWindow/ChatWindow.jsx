import { useEffect, useRef, useState, useCallback } from 'react';
import './ChatWindow.css';
import MessageBubble      from '../MessageBubble/MessageBubble';
import ToolResultBubble   from '../ToolResultBubble/ToolResultBubble';
import CommentaryStream   from '../CommentaryStream/CommentaryStream';
import WelcomeCapsules    from '../WelcomeCapsules/WelcomeCapsules';
import ToolSelector       from '../ToolSelector/ToolSelector';
import { useStreamingChat } from '../../hooks/useStreamingChat';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';
import { db } from '../../firebase';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function ChatWindow({ chat, user, onFirstMessage }) {
  const bottomRef = useRef(null);
  const [tools,    setTools]   = useState([]);
  const [error,    setError]   = useState('');
  const [turns,    setTurns]   = useState([]); // [{id, userMsg, toolResult, commentary, toolId, streaming}]
  const { streaming, sendMessage } = useStreamingChat();
  const streamingRef = useRef(streaming);

  useEffect(() => {
    streamingRef.current = streaming;
  }, [streaming]);

  // Fetch tool list on mount
  useEffect(() => {
    fetch(`${API_BASE}/tools`)
      .then((r) => r.json())
      .then((d) => setTools(d.tools || []))
      .catch(() => {});
  }, []);

  // Subscribe to real-time messages for the active chat from Firestore
  useEffect(() => {
    if (!chat?.id || !user?.uid) {
      setTurns([]);
      setError('');
      return;
    }

    const q = query(
      collection(db, 'users', user.uid, 'chats', chat.id, 'messages'),
      orderBy('createdAt', 'asc')
    );

    const unsub = onSnapshot(q, (snap) => {
      // If user is currently streaming a live response, do not overwrite state mid-stream
      if (streamingRef.current) return;

      const loadedTurns = [];
      let currentTurn = null;

      snap.docs.forEach((docSnap) => {
        const data = docSnap.data();
        if (data.role === 'user') {
          currentTurn = {
            id: docSnap.id,
            userMsg: data.text || '',
            toolId: null,
            toolResult: null,
            toolLoading: false,
            commentary: '',
            commentaryStreaming: false,
          };
          loadedTurns.push(currentTurn);
        } else if (data.role === 'assistant') {
          if (!currentTurn) {
            currentTurn = {
              id: docSnap.id,
              userMsg: '',
              toolId: null,
              toolResult: null,
              toolLoading: false,
              commentary: '',
              commentaryStreaming: false,
            };
            loadedTurns.push(currentTurn);
          }
          currentTurn.toolId = data.toolUsed || null;
          if (data.toolResult) {
            // Handle if stored as full object or raw result
            currentTurn.toolResult = data.toolResult.tool_id
              ? data.toolResult
              : {
                  tool_id: data.toolUsed,
                  display_name: data.toolUsed ? data.toolUsed.toUpperCase() : 'Tool',
                  base_model: '',
                  fine_tune_dataset: '',
                  result: data.toolResult,
                };
          }
          currentTurn.commentary = data.text || '';
        }
      });

      setTurns(loadedTurns);
    });

    return unsub;
  }, [chat?.id, user?.uid]);

  // Auto-scroll to bottom on turns update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns]);

  const isEmpty = turns.length === 0;

  const handleSend = useCallback(async ({ message, toolId, toolInput }) => {
    if (!chat) return;
    setError('');

    // Create a new turn slot
    const turnId = Date.now();
    setTurns((prev) => [
      ...prev,
      {
        id: turnId,
        userMsg: message,
        toolId,
        toolInput,
        toolResult: null,
        toolLoading: !!toolId,
        commentary: '',
        commentaryStreaming: true,
      },
    ]);

    if (isEmpty) onFirstMessage?.(message);

    const updateTurn = (patch) =>
      setTurns((prev) =>
        prev.map((t) => (t.id === turnId ? { ...t, ...(typeof patch === 'function' ? patch(t) : patch) } : t))
      );

    await sendMessage({
      chatId:   chat.id,
      message,
      toolId,
      toolInput,
      onToolResult: (ev) =>
        updateTurn({ toolResult: ev, toolLoading: false }),
      onCommentaryChunk: (text) =>
        updateTurn((t) => ({
          commentary: (t.commentary || '') + text,
          commentaryStreaming: true,
        })),
      onDone: () =>
        updateTurn({ commentaryStreaming: false, toolLoading: false }),
      onError: (msg) => {
        setError(msg);
        updateTurn({ commentaryStreaming: false, toolLoading: false });
      },
    });
  }, [chat, isEmpty, onFirstMessage, sendMessage]);

  const handleRetry = useCallback(async (turn) => {
    if (!chat) return;
    setTurns((prev) => prev.filter((t) => t.id !== turn.id));
    await handleSend({
      message:   turn.userMsg,
      toolId:    turn.toolId,
      toolInput: turn.toolInput,
    });
  }, [chat, handleSend]);

  if (!chat) {
    return (
      <div className="chat-window" style={{ background: 'var(--clr-bg)' }}>
        <div className="no-chat-selected">
          <div className="no-chat-selected-icon">💬</div>
          Select or create a chat to get started
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {/* Messages area */}
      <div className="chat-messages">
        {isEmpty ? (
          <WelcomeCapsules />
        ) : (
          turns.map((turn) => (
            <div key={turn.id} className="fade-in-up">
              {/* User bubble */}
              {turn.userMsg && <MessageBubble text={turn.userMsg} />}

              {/* Tool result bubble */}
              {(turn.toolLoading || turn.toolResult) && (
                <ToolResultBubble
                  toolResult={turn.toolResult}
                  loading={turn.toolLoading}
                />
              )}

              {/* Streamed commentary */}
              <CommentaryStream
                text={turn.commentary}
                streaming={turn.commentaryStreaming}
                onRetry={!turn.commentaryStreaming ? () => handleRetry(turn) : undefined}
              />
            </div>
          ))
        )}

        {error && (
          <div className="error-banner" role="alert">
            ⚠ {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Tool selector + input */}
      <ToolSelector
        tools={tools}
        streaming={streaming}
        onSend={handleSend}
      />
    </div>
  );
}
