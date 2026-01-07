import { useState } from 'react';
import './MessageInput.css';

function MessageInput({ onSend, disabled, onEnd, onShowHistory }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="message-input-container">
      <div className="input-actions-top">
        <button 
          type="button" 
          className="btn btn-text btn-small"
          onClick={onShowHistory}
        >
          View History
        </button>
        <button 
          type="button" 
          className="btn btn-text btn-small"
          onClick={onEnd}
        >
          End Session
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your response..."
            className="message-input"
            rows="1"
            disabled={disabled}
          />
          <button 
            type="submit" 
            className="btn btn-send"
            disabled={!input.trim() || disabled}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}

export default MessageInput;
