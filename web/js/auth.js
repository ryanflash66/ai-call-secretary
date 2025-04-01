/**
 * Authentication module for the AI Call Secretary web interface.
 * Handles user login, logout, token management, password management,
 * and security features.
 */

// Global variables
let AUTH_TOKEN = null;
let REFRESH_TOKEN = null;
let USER_DATA = null;
let TOKEN_REFRESH_TIMER = null;
const TOKEN_REFRESH_INTERVAL = 15 * 60 * 1000; // 15 minutes

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Try to load token from localStorage
  AUTH_TOKEN = localStorage.getItem('auth_token');
  REFRESH_TOKEN = localStorage.getItem('refresh_token');
  
  // Parse user data if available
  const userData = localStorage.getItem('user_data');
  if (userData) {
    try {
      USER_DATA = JSON.parse(userData);
    } catch (e) {
      console.error('Error parsing user data:', e);
      USER_DATA = null;
    }
  }
  
  // Initialize login form
  initLoginForm();
  
  // Check token and start session
  checkAndRefreshToken();
});

// Initialize login form
function initLoginForm() {
  const loginForm = document.getElementById('login-form');
  if (!loginForm) return;
  
  loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('remember-me')?.checked || false;
    
    login(username, password, rememberMe);
  });
  
  // Password reset link
  const resetLink = document.getElementById('password-reset-link');
  if (resetLink) {
    resetLink.addEventListener('click', function(e) {
      e.preventDefault();
      openModal('password-reset-modal');
    });
  }
  
  // Password reset form
  const resetForm = document.getElementById('password-reset-form');
  if (resetForm) {
    resetForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const email = document.getElementById('reset-email').value;
      requestPasswordReset(email);
    });
  }
}

// Check token validity and refresh if needed
function checkAndRefreshToken() {
  if (!AUTH_TOKEN) {
    // No token, show login
    showLoginForm();
    return;
  }
  
  // Check token
  fetchWithAuth(`${API_BASE_URL}/security/users/${USER_DATA?.username || 'me'}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Invalid token');
      }
      return response.json();
    })
    .then(userData => {
      // Update user data
      USER_DATA = userData;
      localStorage.setItem('user_data', JSON.stringify(userData));
      
      // Start refresh timer
      startTokenRefreshTimer();
      
      // Initialize UI
      initUI();
      
      // Check system status
      checkSystemStatus();
      
      // Initialize WebSocket connection if available
      if (typeof initWebSocket === 'function') {
        initWebSocket();
      }
    })
    .catch(error => {
      console.error('Token validation error:', error);
      
      // Try to refresh token
      if (REFRESH_TOKEN) {
        refreshToken();
      } else {
        // Clear invalid tokens and show login
        clearAuthData();
        showLoginForm();
      }
    });
}

// Start token refresh timer
function startTokenRefreshTimer() {
  // Clear existing timer
  if (TOKEN_REFRESH_TIMER) {
    clearTimeout(TOKEN_REFRESH_TIMER);
  }
  
  // Set new timer
  TOKEN_REFRESH_TIMER = setTimeout(refreshToken, TOKEN_REFRESH_INTERVAL);
}

// Refresh token
function refreshToken() {
  if (!REFRESH_TOKEN) {
    clearAuthData();
    showLoginForm();
    return;
  }
  
  fetch(`${API_BASE_URL}/security/token/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ refresh_token: REFRESH_TOKEN })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
      return response.json();
    })
    .then(data => {
      // Update tokens
      AUTH_TOKEN = data.access_token;
      REFRESH_TOKEN = data.refresh_token;
      USER_DATA = data.user;
      
      // Save tokens
      localStorage.setItem('auth_token', AUTH_TOKEN);
      localStorage.setItem('refresh_token', REFRESH_TOKEN);
      localStorage.setItem('user_data', JSON.stringify(USER_DATA));
      
      // Restart refresh timer
      startTokenRefreshTimer();
    })
    .catch(error => {
      console.error('Token refresh error:', error);
      clearAuthData();
      showLoginForm();
    });
}

// Login function
function login(username, password, rememberMe = false) {
  showLoginLoading(true);
  
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  fetch(`${API_BASE_URL}/security/token`, {
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
      // Store tokens
      AUTH_TOKEN = data.access_token;
      REFRESH_TOKEN = data.refresh_token;
      USER_DATA = data.user;
      
      // Save tokens if remember me is checked
      if (rememberMe) {
        localStorage.setItem('auth_token', AUTH_TOKEN);
        localStorage.setItem('refresh_token', REFRESH_TOKEN);
        localStorage.setItem('user_data', JSON.stringify(USER_DATA));
      }
      
      // Start token refresh timer
      startTokenRefreshTimer();
      
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
    })
    .finally(() => {
      showLoginLoading(false);
    });
}

// Logout function
function logout(manual = true) {
  // Send logout request if we have a token
  if (AUTH_TOKEN) {
    fetchWithAuth(`${API_BASE_URL}/security/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ refresh_token: REFRESH_TOKEN })
    }).catch(error => {
      console.error('Logout error:', error);
    });
  }
  
  // Clear auth data
  clearAuthData();
  
  // Close WebSocket connection if available
  if (typeof wsClient !== 'undefined' && wsClient) {
    wsClient.close();
  }
  
  // Show login form
  showLoginForm();
  
  // Show notification if manual logout
  if (manual) {
    showNotification('Logged out successfully', 'info');
  }
}

// Clear authentication data
function clearAuthData() {
  AUTH_TOKEN = null;
  REFRESH_TOKEN = null;
  USER_DATA = null;
  
  localStorage.removeItem('auth_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_data');
  
  if (TOKEN_REFRESH_TIMER) {
    clearTimeout(TOKEN_REFRESH_TIMER);
    TOKEN_REFRESH_TIMER = null;
  }
}

// Show login form
function showLoginForm() {
  openModal('login-modal');
  
  // Clear any previous error
  document.getElementById('login-error').textContent = '';
  
  // Reset form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.reset();
  }
}

// Toggle loading state on login form
function showLoginLoading(loading) {
  const submitButton = document.querySelector('#login-form button[type="submit"]');
  const loadingIndicator = document.getElementById('login-loading');
  
  if (submitButton) {
    submitButton.disabled = loading;
  }
  
  if (loadingIndicator) {
    loadingIndicator.style.display = loading ? 'inline-block' : 'none';
  }
}

// Request password reset
function requestPasswordReset(email) {
  const resetButton = document.querySelector('#password-reset-form button[type="submit"]');
  const resetStatus = document.getElementById('reset-status');
  
  if (resetButton) {
    resetButton.disabled = true;
  }
  
  if (resetStatus) {
    resetStatus.textContent = 'Sending request...';
    resetStatus.className = 'status-info';
  }
  
  fetch(`${API_BASE_URL}/security/password/reset`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Error requesting password reset');
      }
      
      if (resetStatus) {
        resetStatus.textContent = 'Password reset link sent to your email.';
        resetStatus.className = 'status-success';
      }
      
      // Reset form
      document.getElementById('password-reset-form').reset();
      
      // Close modal after delay
      setTimeout(() => {
        closeModal('password-reset-modal');
      }, 2000);
    })
    .catch(error => {
      console.error('Password reset error:', error);
      
      if (resetStatus) {
        resetStatus.textContent = error.message;
        resetStatus.className = 'status-error';
      }
    })
    .finally(() => {
      if (resetButton) {
        resetButton.disabled = false;
      }
    });
}

// Change password
function changePassword(currentPassword, newPassword, confirmPassword) {
  if (!USER_DATA) {
    showNotification('You must be logged in to change your password', 'error');
    return Promise.reject(new Error('Not logged in'));
  }
  
  if (newPassword !== confirmPassword) {
    return Promise.reject(new Error('New passwords do not match'));
  }
  
  return fetchWithAuth(`${API_BASE_URL}/security/users/${USER_DATA.username}/password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(data => {
          throw new Error(data.detail || 'Error changing password');
        });
      }
      
      showNotification('Password changed successfully', 'success');
      return true;
    });
}

// Fetch with authentication
function fetchWithAuth(url, options = {}) {
  if (!AUTH_TOKEN) {
    return Promise.reject(new Error('No authentication token'));
  }
  
  // Add authorization header
  const headers = options.headers || {};
  headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  
  // Add CSRF token if available
  const csrfToken = getCsrfToken();
  if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)) {
    headers['X-CSRF-Token'] = csrfToken;
  }
  
  return fetch(url, {
    ...options,
    headers
  }).then(response => {
    // Handle 401 (Unauthorized) by refreshing token or logging out
    if (response.status === 401 && REFRESH_TOKEN) {
      return refreshTokenAndRetry(url, options);
    }
    return response;
  });
}

// Refresh token and retry request
function refreshTokenAndRetry(url, options) {
  return fetch(`${API_BASE_URL}/security/token/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ refresh_token: REFRESH_TOKEN })
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
      return response.json();
    })
    .then(data => {
      // Update tokens
      AUTH_TOKEN = data.access_token;
      REFRESH_TOKEN = data.refresh_token;
      USER_DATA = data.user;
      
      // Save tokens
      localStorage.setItem('auth_token', AUTH_TOKEN);
      localStorage.setItem('refresh_token', REFRESH_TOKEN);
      localStorage.setItem('user_data', JSON.stringify(USER_DATA));
      
      // Restart refresh timer
      startTokenRefreshTimer();
      
      // Retry original request with new token
      const headers = options.headers || {};
      headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
      
      return fetch(url, {
        ...options,
        headers
      });
    })
    .catch(error => {
      console.error('Token refresh error:', error);
      logout(false);
      throw error;
    });
}

// Get CSRF token from cookie
function getCsrfToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrf_token') {
      return value;
    }
  }
  return null;
}

// Check if user is authenticated
function isAuthenticated() {
  return AUTH_TOKEN !== null && USER_DATA !== null;
}

// Get current user data
function getCurrentUser() {
  return USER_DATA;
}

// Check if user has specified role
function hasRole(role) {
  return USER_DATA && USER_DATA.role === role;
}

// Expose public functions
window.auth = {
  login,
  logout,
  isAuthenticated,
  getCurrentUser,
  hasRole,
  fetchWithAuth,
  changePassword,
  requestPasswordReset
};