/**
 * Authentication module for the AI Call Secretary web interface.
 * Handles user login, logout, and token management.
 */

// Check if user is authenticated
function isAuthenticated() {
  return AUTH_TOKEN !== null;
}

// Handle login form submission
document.getElementById('login-form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  login(username, password);
});

// Login function
function login(username, password) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Invalid username or password');
    }
    return response.json();
  })
  .then(data => {
    // Store token
    AUTH_TOKEN = data.access_token;
    localStorage.setItem('auth_token', AUTH_TOKEN);
    
    // Close login modal
    closeModal('login-modal');
    
    // Initialize UI
    initUI();
    
    // Check system status
    checkSystemStatus();
    
    // Initialize WebSocket connection if available
    if (typeof initWebSocket === 'function') {
      initWebSocket();
    }
    
    // Show notification
    showNotification('Login successful', 'success');
  })
  .catch(error => {
    // Show error message
    document.getElementById('login-error').textContent = error.message;
    console.error('Login error:', error);
  });
}

// Logout function
function logout() {
  // Clear token
  AUTH_TOKEN = null;
  localStorage.removeItem('auth_token');
  
  // Close WebSocket connection if available
  if (typeof wsClient !== 'undefined' && wsClient) {
    wsClient.close();
  }
  
  // Show login modal
  openModal('login-modal');
  
  // Show notification
  showNotification('Logged out successfully', 'info');
}

// Check token validity
function checkToken() {
  if (!AUTH_TOKEN) return Promise.resolve(false);
  
  return fetch(`${API_BASE_URL}/status`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${AUTH_TOKEN}`
    }
  })
  .then(response => {
    if (!response.ok) {
      // Token is invalid, clear it
      AUTH_TOKEN = null;
      localStorage.removeItem('auth_token');
      return false;
    }
    return true;
  })
  .catch(() => {
    // Error checking token, assume it's invalid
    AUTH_TOKEN = null;
    localStorage.removeItem('auth_token');
    return false;
  });
}