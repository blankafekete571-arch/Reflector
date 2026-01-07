import { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import ProgressBar from './ProgressBar';
import HistoryModal from './HistoryModal';
import './ChatWindow.css';

function ChatWindow({ sessionId, onComplete, onEnd }) {
  const [messages, setMessages] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [stepTitle, setStepTitle] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [initialMessage, setInitialMessage] = useState('');
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load initial session state
    const loadSession = async () => {
      try {
        const data = await api.getSessionState(sessionId);
        setCurrentStep(data.current_step);
        setStepTitle(data.step_title);
        
        if (data.assistant_response) {
          setInitialMessage(data.assistant_response);
          setMessages([{
            type: 'assistant',
            content: data.assistant_response,
            timestamp: new Date(),
          }]);
        }
      } catch (err) {
        console.error('Failed to load session:', err);
      }
    };

    loadSession();
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (message) => {
    // Add user message
    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Show typing indicator
    setIsTyping(true);

    try {
      const data = await api.sendMessage(sessionId, message);
      
      // Remove typing indicator and add assistant response
      setIsTyping(false);
      const assistantMessage = {
        type: 'assistant',
        content: data.assistant_response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Update progress
      setCurrentStep(data.current_step);
      setStepTitle(data.step_title);

      // Check if complete
      if (data.is_complete) {
        setIsComplete(true);
        setTimeout(() => {
          onComplete();
        }, 2000);
      }
    } catch (err) {
      setIsTyping(false);
      console.error('Failed to send message:', err);
      // Add error message
      const errorMessage = {
        type: 'error',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleEndSession = () => {
    if (window.confirm('Are you sure you want to end this reflection session?')) {
      api.endSession(sessionId).catch(console.error);
      onEnd();
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 16v-4"></path>
            <path d="M12 8h.01"></path>
          </svg>
          <h1>Reflektor</h1>
        </div>
      </div>

      <ProgressBar currentStep={currentStep} stepTitle={stepTitle} totalSteps={8} />

      <div className="chat-container">
        <MessageList 
          messages={messages} 
          isTyping={isTyping}
          messagesEndRef={messagesEndRef}
        />
        
        <MessageInput 
          onSend={handleSendMessage} 
          disabled={isComplete}
          onEnd={handleEndSession}
          onShowHistory={() => setShowHistory(true)}
        />
      </div>

      {showHistory && (
        <HistoryModal 
          sessionId={sessionId}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
}

export default ChatWindow;
