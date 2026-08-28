import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './CommentaryStream.css';

export default function CommentaryStream({ text, streaming, onRetry }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (!text && !streaming) return null;

  return (
    <div className="commentary-wrapper">
      <div className={`commentary-text${streaming && !text ? ' typing-cursor' : ''}`}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {text}
        </ReactMarkdown>
        {streaming && text && <span className="typing-cursor" aria-hidden="true" />}
      </div>

      {/* Always-visible actions (Gray monochrome SVG icons) */}
      {!streaming && text && (
        <div className="commentary-actions">
          <button
            id="copy-commentary-btn"
            className="commentary-action-btn"
            onClick={copy}
            aria-label="Copy response"
            title="Copy response"
          >
            {copied ? (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--clr-success)' }}>
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span>Copied</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
                <span>Copy</span>
              </>
            )}
          </button>

          {onRetry && (
            <button
              id="retry-btn"
              className="commentary-action-btn"
              onClick={onRetry}
              aria-label="Try again"
              title="Try again"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
              <span>Try again</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
