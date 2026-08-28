import './WelcomeCapsules.css';

const TOOL_CAPSULES = [
  {
    id: 'general',
    name: 'General Chat',
    desc: 'Ask general questions, get explanations, code, or brainstorming.',
    model: 'DeepSeek-V3',
  },
  {
    id: 'sentiment',
    name: 'Sentiment Analyzer',
    desc: 'Paste any text to see whether it reads as Positive or Negative.',
    model: 'DistilBERT · SST-2',
  },
  {
    id: 'topic',
    name: 'Topic Classifier',
    desc: 'Snaps headlines or articles into World, Sports, Business, or Sci/Tech.',
    model: 'DistilBERT · AG News',
  },
  {
    id: 'ner',
    name: 'Named Entity Recognizer',
    desc: 'Highlights people, organisations, and locations mentioned in text.',
    model: 'BERT · CoNLL-2003',
  },
  {
    id: 'summarization',
    name: 'Text Summarizer',
    desc: 'Paste a long article or passage and get a concise summary in seconds.',
    model: 'T5-small · CNN/DailyMail',
  },
  {
    id: 'qa',
    name: 'Question Answering',
    desc: 'Provide a context passage and ask a question to extract the answer span.',
    model: 'DistilBERT · SQuAD v1.1',
  },
];

export default function WelcomeCapsules() {
  return (
    <div className="welcome-container">
      <h1 className="welcome-title">Welcome to TextSphere</h1>
      <p className="welcome-subtitle">
        Chat with five fine-tuned NLP models or use General Chat. Select a tool from the bar below before sending a task.
      </p>

      <div className="capsules-grid">
        {TOOL_CAPSULES.map((t) => (
          <div key={t.id} className="capsule">
            <div className="capsule-name">{t.name}</div>
            <div className="capsule-desc">{t.desc}</div>
            <div className="capsule-model">{t.model}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
