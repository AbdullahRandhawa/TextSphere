import { useState } from 'react';
import './Sidebar.css';

function formatDate(ts) {
  if (!ts) return '';
  const d = ts.toDate ? ts.toDate() : new Date(ts);
  const now = new Date();
  const diff = (now - d) / 1000;
  if (diff < 60)      return 'just now';
  if (diff < 3600)    return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400)   return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800)  return d.toLocaleDateString(undefined, { weekday: 'short' });
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function getInitial(user) {
  return (user?.displayName || user?.email || '?').charAt(0).toUpperCase();
}

export default function Sidebar({
  user,
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onRenameChat,
  onLogout,
}) {
  const [renamingId, setRenamingId] = useState(null);
  const [renameVal,  setRenameVal]  = useState('');

  const startRename = (chat, e) => {
    e.stopPropagation();
    setRenamingId(chat.id);
    setRenameVal(chat.title || '');
  };

  const commitRename = (id) => {
    if (renameVal.trim()) onRenameChat(id, renameVal.trim());
    setRenamingId(null);
  };

  return (
    <aside className="sidebar" aria-label="Chat sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🌐</div>
          <span className="sidebar-logo-name">TextSphere</span>
        </div>
        <button
          id="new-chat-btn"
          className="btn sidebar-new-chat"
          onClick={onNewChat}
          aria-label="Start a new chat"
        >
          + New Chat
        </button>
      </div>

      <nav className="sidebar-list" aria-label="Chat history">
        {chats.length === 0 ? (
          <div className="sidebar-empty">
            No chats yet.<br />Click <strong>New Chat</strong> to start.
          </div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`sidebar-item${chat.id === activeChatId ? ' active' : ''}`}
              onClick={() => onSelectChat(chat.id)}
              role="button"
              tabIndex={0}
              aria-current={chat.id === activeChatId ? 'page' : undefined}
              onKeyDown={(e) => e.key === 'Enter' && onSelectChat(chat.id)}
            >
              <div className="sidebar-item-info">
                {renamingId === chat.id ? (
                  <input
                    className="input"
                    value={renameVal}
                    autoFocus
                    onChange={(e) => setRenameVal(e.target.value)}
                    onBlur={() => commitRename(chat.id)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') commitRename(chat.id);
                      if (e.key === 'Escape') setRenamingId(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    style={{ padding: '2px 6px', fontSize: '13px' }}
                  />
                ) : (
                  <>
                    <div className="sidebar-item-title">{chat.title || 'Untitled'}</div>
                    <div className="sidebar-item-date">{formatDate(chat.updatedAt)}</div>
                  </>
                )}
              </div>
              <div className="sidebar-item-actions">
                <button
                  className="btn-icon"
                  title="Rename"
                  onClick={(e) => startRename(chat, e)}
                  aria-label="Rename chat"
                >✏️</button>
                <button
                  className="btn-icon"
                  title="Delete"
                  onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }}
                  aria-label="Delete chat"
                  style={{ color: 'var(--clr-error)' }}
                >🗑</button>
              </div>
            </div>
          ))
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user-avatar">{getInitial(user)}</div>
        <div className="sidebar-user-info">
          <div className="sidebar-user-name">{user?.displayName || 'User'}</div>
          <div className="sidebar-user-email">{user?.email}</div>
        </div>
        <button
          id="logout-btn"
          className="btn-icon"
          onClick={onLogout}
          title="Sign out"
          aria-label="Sign out"
          style={{ color: 'var(--clr-text-3)' }}
        >⏏</button>
      </div>
    </aside>
  );
}
