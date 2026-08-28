import { useState, useCallback } from 'react';
import './Chat.css';
import { useAuth }   from '../hooks/useAuth';
import { useChats }  from '../hooks/useChats';
import Sidebar       from '../components/Sidebar/Sidebar';
import ChatWindow    from '../components/ChatWindow/ChatWindow';
import { doc, updateDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../firebase';

export default function Chat() {
  const { user, logout }                         = useAuth();
  const { chats, createChat, renameChat, deleteChat } = useChats(user);
  const [activeChatId, setActiveChatId]          = useState(null);
  const [chatError, setChatError]                = useState('');

  const activeChat = chats.find((c) => c.id === activeChatId) ?? null;

  const handleNewChat = useCallback(async () => {
    setChatError('');
    try {
      const id = await createChat('New Chat');
      setActiveChatId(id);
    } catch (err) {
      setChatError(err.message);
    }
  }, [createChat]);

  const handleSelectChat = useCallback((id) => {
    setActiveChatId(id);
    setChatError('');
  }, []);

  const handleDeleteChat = useCallback(async (id) => {
    await deleteChat(id);
    if (activeChatId === id) setActiveChatId(null);
  }, [deleteChat, activeChatId]);

  // When first message is sent in a new chat, update the chat title
  const handleFirstMessage = useCallback(async (msg) => {
    if (!activeChatId || !user) return;
    const title = msg.slice(0, 60);
    try {
      await updateDoc(doc(db, 'users', user.uid, 'chats', activeChatId), {
        title,
        updatedAt: serverTimestamp(),
      });
    } catch {}
  }, [activeChatId, user]);

  return (
    <div className="chat-page">
      <Sidebar
        user={user}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onRenameChat={renameChat}
        onLogout={logout}
      />

      <main className="chat-main">
        {chatError && (
          <div style={{
            padding: '10px 24px',
            background: 'var(--clr-error-glow)',
            color: 'var(--clr-error)',
            fontSize: 13,
            borderBottom: '1px solid rgba(248,113,113,0.3)',
          }}>
            ⚠ {chatError}
          </div>
        )}
        <ChatWindow
          chat={activeChat}
          user={user}
          onFirstMessage={handleFirstMessage}
        />
      </main>
    </div>
  );
}
