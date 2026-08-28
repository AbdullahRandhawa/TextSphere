import '../MessageBubble/MessageBubble.css';

// Renders per-tool structured output inside the bordered card
function ToolOutput({ toolId, result }) {
  switch (toolId) {
    case 'sentiment': {
      const isPos = result.label === 'Positive';
      return (
        <div className="result-sentiment">
          <span className={isPos ? 'result-label-positive' : 'result-label-negative'}>
            {isPos ? '😊' : '😞'} {result.label}
          </span>
          <span className="result-confidence">
            Confidence: {(result.confidence * 100).toFixed(1)}%
          </span>
        </div>
      );
    }
    case 'topic':
      return (
        <div>
          <div className="result-topic">📂 {result.label}</div>
          <div className="result-confidence" style={{ marginTop: 6 }}>
            Confidence: {(result.confidence * 100).toFixed(1)}%
          </div>
        </div>
      );
    case 'ner':
      return result.entities?.length ? (
        <div className="result-entities">
          {result.entities.map((ent, i) => (
            <span key={i} className="entity-tag">
              <span className={`entity-label entity-${ent.label}`}>{ent.label}</span>
              {ent.text}
            </span>
          ))}
        </div>
      ) : (
        <div className="result-no-entities">No named entities found.</div>
      );
    case 'summarization':
      return <div className="result-summary">{result.summary}</div>;
    case 'qa':
      return (
        <div>
          <div className="result-answer">"{result.answer}"</div>
          <div className="result-answer-conf">
            Confidence: {(result.confidence * 100).toFixed(1)}%
          </div>
        </div>
      );
    default:
      return <pre style={{ fontSize: 12, color: 'var(--clr-text-2)' }}>{JSON.stringify(result, null, 2)}</pre>;
  }
}

export default function ToolResultBubble({ toolResult, loading }) {
  if (loading) {
    return (
      <div className="tool-result-wrapper">
        <div className="tool-result-card">
          <div className="tool-loading">
            <div className="spinner" />
            Running model…
          </div>
        </div>
      </div>
    );
  }

  if (!toolResult) return null;

  const chipClass = `chip chip-${toolResult.tool_id}`;

  return (
    <div className="tool-result-wrapper">
      <div className="tool-result-card">
        <div className="tool-result-header">
          <span className={chipClass}>🔬 {toolResult.display_name}</span>
          <span className="tool-model-badge">
            {toolResult.base_model} · {toolResult.fine_tune_dataset}
          </span>
        </div>
        <div className="tool-result-body">
          <ToolOutput toolId={toolResult.tool_id} result={toolResult.result} />
        </div>
      </div>
    </div>
  );
}
