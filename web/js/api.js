/**
 * API client for the AI Call Secretary web interface.
 * Handles communication with the backend API.
 */

// API client class
class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
  
  // General request method with authentication
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Set default headers
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    // Add authentication header if token is available
    if (AUTH_TOKEN) {
      headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
    }
    
    // Merge options
    const requestOptions = {
      ...options,
      headers
    };
    
    try {
      const response = await fetch(url, requestOptions);
      
      // Handle unauthorized
      if (response.status === 401) {
        AUTH_TOKEN = null;
        localStorage.removeItem('auth_token');
        openModal('login-modal');
        throw new Error('Unauthorized - Please log in again');
      }
      
      // Handle other error statuses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }
      
      // Parse JSON response if there is one
      if (response.status !== 204) { // No content
        return await response.json();
      }
      
      return null;
    } catch (error) {
      console.error(`API request failed: ${error.message}`);
      throw error;
    }
  }
  
  // GET request
  async get(endpoint, params = {}) {
    // Build query string
    const queryString = Object.keys(params)
      .filter(key => params[key] !== undefined && params[key] !== null)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    return this.request(url, { method: 'GET' });
  }
  
  // POST request
  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }
  
  // PUT request
  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }
  
  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
  
  // Specific API endpoints
  
  // Call endpoints
  async getCalls(filters = {}) {
    return this.get('/calls', filters);
  }
  
  async getCall(callId) {
    return this.get(`/calls/${callId}`);
  }
  
  async deleteCall(callId) {
    return this.delete(`/calls/${callId}`);
  }
  
  // Action endpoints
  async executeAction(actionType, params = {}) {
    return this.post('/actions', {
      action_type: actionType,
      params
    });
  }
  
  // Appointment endpoints
  async getAppointments(filters = {}) {
    return this.get('/appointments', filters);
  }
  
  async getAppointment(appointmentId) {
    return this.get(`/appointments/${appointmentId}`);
  }
  
  async createAppointment(appointmentData) {
    return this.post('/appointments', appointmentData);
  }
  
  async updateAppointment(appointmentId, appointmentData) {
    return this.put(`/appointments/${appointmentId}`, appointmentData);
  }
  
  async deleteAppointment(appointmentId) {
    return this.delete(`/appointments/${appointmentId}`);
  }
  
  // Message endpoints
  async getMessages(filters = {}) {
    return this.get('/messages', filters);
  }
  
  async getMessage(messageId) {
    return this.get(`/messages/${messageId}`);
  }
  
  async createMessage(messageData) {
    return this.post('/messages', messageData);
  }
  
  async deleteMessage(messageId) {
    return this.delete(`/messages/${messageId}`);
  }
  
  // System and settings endpoints
  async getSystemStatus() {
    return this.get('/status');
  }
  
  async getSettings() {
    return this.get('/settings');
  }
  
  async updateSettings(section, data) {
    return this.put(`/settings/${section}`, data);
  }
  
  async updateUserSettings(data) {
    return this.put('/user/settings', data);
  }
  
  async getVoices(engine) {
    return this.get(`/voice/engines/${engine}/voices`);
  }
  
  async getModels(provider) {
    return this.get(`/llm/providers/${provider}/models`);
  }
  
  // Statistics endpoints
  async getStatistics(type) {
    return this.get(`/statistics/${type}`);
  }
}

// Create global API client instance
const api = new ApiClient(API_BASE_URL);