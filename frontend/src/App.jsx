import { useState } from 'react';
import WelcomeScreen from './components/WelcomeScreen';
import ChatWindow from './components/ChatWindow';
import CompletionScreen from './components/CompletionScreen';
import './App.css';

function App() {
  const [screen, setScreen] = useState('welcome'); // 'welcome', 'chat', 'complete'
  const [sessionId, setSessionId] = useState(null);

  const handleStartSession = (newSessionId) => {
    setSessionId(newSessionId);
    setScreen('chat');
  };

  const handleSessionComplete = () => {
    setScreen('complete');
  };

  const handleNewSession = () => {
    setSessionId(null);
    setScreen('welcome');
  };

  return (
    <div className="app">
      {screen === 'welcome' && (
        <WelcomeScreen onStart={handleStartSession} />
      )}
      {screen === 'chat' && (
        <ChatWindow 
          sessionId={sessionId} 
          onComplete={handleSessionComplete}
          onEnd={handleNewSession}
        />
      )}
      {screen === 'complete' && (
        <CompletionScreen 
          sessionId={sessionId}
          onNewSession={handleNewSession} 
        />
      )}
    </div>
  );
}

export default App;
