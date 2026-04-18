import { useState } from 'react';
import api from '../services/api';
import './CompletionScreen.css';

function CompletionScreen({ sessionId, onNewSession }) {
  const [showHistory, setShowHistory] = useState(false);

  const handleViewHistory = async () => {
    try {
      const data = await api.getHistory(sessionId);
      console.log('History:', data);
      // Could open a modal here or navigate to a history view
      alert('History loaded! Check the console for details.');
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  return (
    <div className="completion-screen">
      <div className="completion-container">
        <div className="completion-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        
        <h2>Reflection Complete</h2>
        <p className="completion-message">
          Thank you for taking the time to reflect on your experience. 
          Your insights and self-awareness are valuable steps in your journey.
        </p>
        
        <div className="completion-actions">
          <button className="btn btn-secondary" onClick={handleViewHistory}>
            View Full History
          </button>
          <button className="btn btn-primary" onClick={onNewSession}>
            Start New Reflection
          </button>
        </div>
      </div>
    </div>
  );
}

export default CompletionScreen;
