import { useState, useEffect, useRef } from 'react';
import '../WelcomeCapsules/WelcomeCapsules.css';

function buildDefaultInput(tool) {
  if (!tool) return { text: '' };
  const props = tool.input_schema?.properties || {};
  return Object.fromEntries(
    Object.entries(props).map(([k, v]) => [k, v.default ?? ''])
  );
}

export default function ToolSelector({ tools, streaming, onSend }) {
  const [selectedId, setSelectedId] = useState(null);
  const [inputs,     setInputs]     = useState({});
  const [error,      setError]      = useState('');
  const textareaRef = useRef(null);

  const selectedTool = tools.find((t) => t.id === selectedId) ?? null;

  // Preserve typed text when switching tools (except QA)
  useEffect(() => {
    setInputs((prev) => {
      const currentText = prev.text || prev.message || prev.context || prev.question || '';
      if (!selectedTool) {
        return { message: currentText };
      }
      if (selectedTool.id === 'qa') {
        return { question: prev.question || '', context: prev.context || currentText };
      }
      const props = selectedTool.input_schema?.properties || {};
      const mainField = Object.keys(props).find((k) => props[k].type === 'string') || 'text';
      return { [mainField]: currentText };
    });
    setError('');
  }, [selectedId]);

  const autoResizeTextarea = (el) => {
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 130) + 'px';
  };

  const collapseTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '42px';
    }
  };

  const setField = (key, val, e) => {
    setInputs((prev) => ({ ...prev, [key]: val }));
    if (e && e.target) {
      autoResizeTextarea(e.target);
    }
  };

  const validate = () => {
    if (!selectedTool) {
      const msg = inputs.message || '';
      if (!msg.trim()) { setError('Please enter a message.'); return null; }
      return { message: msg.trim(), toolId: null, toolInput: null };
    }
    const required = selectedTool.input_schema?.required || [];
    for (const field of required) {
      if (!inputs[field]?.trim()) {
        setError(`"${selectedTool.input_schema.properties[field]?.title || field}" is required.`);
        return null;
      }
    }
    const toolInput = {};
    for (const [k, v] of Object.entries(inputs)) {
      if (v !== '' && v !== undefined) toolInput[k] = v;
    }
    const message = inputs.question
      ? `[Question: ${inputs.question}] [Context: ${inputs.context?.slice(0, 100)}…]`
      : (inputs.text || '');
    return { message, toolId: selectedTool.id, toolInput };
  };

  const handleSend = () => {
    setError('');
    const payload = validate();
    if (!payload) return;
    onSend(payload);
    // Reset inputs and shrink textarea back to 1 line
    setInputs(buildDefaultInput(selectedTool));
    collapseTextarea();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toolTip = (t) =>
    `${t.description}\n${t.base_model} · Fine-tuned on ${t.fine_tune_dataset}`;

  // SVG Send Icon (Monochrome / Sleek)
  const SendIcon = () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );

  const renderForm = () => {
    if (!selectedTool) {
      const isInputEmpty = !(inputs.message || '').trim();
      return (
        <div className="input-field-wrapper">
          <textarea
            id="chat-message-input"
            ref={textareaRef}
            className="input-textarea"
            rows={1}
            placeholder="Send a message (general chat)…"
            value={inputs.message || ''}
            onChange={(e) => setField('message', e.target.value, e)}
            onKeyDown={handleKeyDown}
            disabled={streaming}
          />
          <button
            id="send-btn"
            className="send-btn-inside"
            onClick={handleSend}
            disabled={streaming || isInputEmpty}
            aria-label="Send message"
          >
            {streaming ? <span className="spinner-sm" /> : <SendIcon />}
          </button>
        </div>
      );
    }

    const props = selectedTool.input_schema?.properties || {};
    const isQA  = selectedTool.id === 'qa';

    if (isQA) {
      const isQAEmpty = !(inputs.question || '').trim() || !(inputs.context || '').trim();
      return (
        <div className="qa-form-container">
          <input
            id="qa-question-input"
            className="input qa-input"
            type="text"
            placeholder={props.question?.description || 'Your question…'}
            value={inputs.question || ''}
            onChange={(e) => setField('question', e.target.value)}
            disabled={streaming}
          />
          <div className="input-field-wrapper">
            <textarea
              id="qa-context-input"
              className="input-textarea"
              rows={2}
              placeholder={props.context?.description || 'Paste context passage here…'}
              value={inputs.context || ''}
              onChange={(e) => setField('context', e.target.value, e)}
              onKeyDown={handleKeyDown}
              disabled={streaming}
            />
            <button
              id="send-btn"
              className="send-btn-inside"
              onClick={handleSend}
              disabled={streaming || isQAEmpty}
              aria-label="Send QA request"
            >
              {streaming ? <span className="spinner-sm" /> : <SendIcon />}
            </button>
          </div>
        </div>
      );
    }

    const mainField = Object.keys(props).find((k) => props[k].type === 'string') || 'text';
    const isToolTextEmpty = !(inputs[mainField] || '').trim();

    return (
      <div className="input-field-wrapper">
        <textarea
          id="tool-text-input"
          ref={textareaRef}
          className="input-textarea"
          rows={1}
          placeholder={props[mainField]?.description || 'Enter text…'}
          value={inputs[mainField] || ''}
          onChange={(e) => setField(mainField, e.target.value, e)}
          onKeyDown={handleKeyDown}
          disabled={streaming}
        />
        <button
          id="send-btn"
          className="send-btn-inside"
          onClick={handleSend}
          disabled={streaming || isToolTextEmpty}
          aria-label={`Run ${selectedTool.display_name}`}
        >
          {streaming ? <span className="spinner-sm" /> : <SendIcon />}
        </button>
      </div>
    );
  };

  return (
    <div className="tool-selector-floating-wrapper">
      <div className="tool-selector-container">
        {/* Tool tabs (compact pills) */}
        <div className="tool-selector-tabs" role="tablist" aria-label="Select NLP tool">
          {tools.map((t) => (
            <button
              key={t.id}
              id={`tool-tab-${t.id}`}
              className={`tool-tab${selectedId === t.id ? ' active' : ''}`}
              onClick={() => setSelectedId(t.id === selectedId ? null : t.id)}
              role="tab"
              aria-selected={selectedId === t.id}
              data-tooltip={toolTip(t)}
            >
              {t.display_name}
            </button>
          ))}
        </div>

        {/* Input form */}
        <div className="tool-input-area">
          {error && (
            <div className="tool-error-hint">
              ⚠ {error}
            </div>
          )}
          {renderForm()}
        </div>
      </div>
    </div>
  );
}
