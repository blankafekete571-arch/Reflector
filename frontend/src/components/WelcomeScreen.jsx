import { useState } from 'react';
import api from '../services/api';
import './WelcomeScreen.css';

function WelcomeScreen({ onStart }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await api.createSession();
      onStart(data.session_id);
    } catch (err) {
      console.error('Failed to start session:', err);
      setError('Failed to start session. Please make sure the server is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="welcome-screen">
      <div className="welcome-container">
        <header className="welcome-header">
          <div className="logo">
            <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M12 16v-4"></path>
              <path d="M12 8h.01"></path>
            </svg>
            <h1>Reflektor</h1>
          </div>
          <p className="tagline">Your structured self-reflection companion</p>
        </header>

        <div className="welcome-content">
          <div className="welcome-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          
          <h2>Welcome to Navigate</h2>
          <p className="welcome-description">
            I'll guide you through a structured self-reflection exercise using CBT techniques. 
            We'll explore a specific situation together through 8 thoughtful steps.
          </p>
          
          <div className="steps-preview">
            <h3>What we'll explore:</h3>
            <ol>
              <li>The situation that occurred</li>
              <li>Physical sensations you noticed</li>
              <li>Automatic thoughts that arose</li>
              <li>Emotions you experienced</li>
              <li>What it meant to you</li>
              <li>Alternative perspectives</li>
              <li>Next steps (optional)</li>
              <li>Reflection closure</li>
            </ol>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            className="btn btn-primary btn-large" 
            onClick={handleStart}
            disabled={loading}
          >
            {loading ? 'Starting...' : 'Begin Reflection'}
          </button>

          <div className="disclaimer">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>This is a self-reflection tool, not therapy. If you're experiencing a crisis, please contact emergency services or a crisis hotline.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WelcomeScreen;
