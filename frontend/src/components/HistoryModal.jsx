import { useState, useEffect } from 'react';
import api from '../services/api';
import './HistoryModal.css';

function HistoryModal({ sessionId, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        const data = await api.getHistory(sessionId);
        setHistory(data.history);
      } catch (err) {
        console.error('Failed to load history:', err);
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [sessionId]);

  const handleDownload = () => {
    const dataStr = JSON.stringify(history, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reflection-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Reflection History</h2>
          <button className="btn-close" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div className="modal-body">
          {loading ? (
            <p className="loading-text">Loading history...</p>
          ) : history.length === 0 ? (
            <p className="empty-text">No history available yet.</p>
          ) : (
            history.map((item, index) => (
              <div key={index} className="history-item">
                <div className="history-step">Step {item.step_id}</div>
                <h3>{item.title}</h3>
                <p className="history-question">{item.question}</p>
                <div className="history-answer">
                  <strong>Your response:</strong>
                  <p>{item.answer}</p>
                </div>
                <div className="history-response">
                  <strong>Reflection:</strong>
                  <p>{item.assistant}</p>
                </div>
              </div>
            ))
          )}
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={handleDownload}>
            Download as JSON
          </button>
        </div>
      </div>
    </div>
  );
}

export default HistoryModal;
