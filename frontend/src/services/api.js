import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = {
  // Health check
  async checkHealth() {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  // Create a new session
  async createSession() {
    const response = await axios.post(`${API_BASE_URL}/sessions`);
    return response.data;
  },

  // Send a message
  async sendMessage(sessionId, message) {
    const response = await axios.post(
      `${API_BASE_URL}/sessions/${sessionId}/respond`,
      { user_input: message }
    );
    return response.data;
  },

  // Get session state
  async getSessionState(sessionId) {
    const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`);
    return response.data;
  },

  // Get session history
  async getHistory(sessionId) {
    const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}/history`);
    return response.data;
  },

  // End session
  async endSession(sessionId, save = false) {
    const response = await axios.delete(
      `${API_BASE_URL}/sessions/${sessionId}?save=${save}`
    );
    return response.data;
  },
};

export default api;
