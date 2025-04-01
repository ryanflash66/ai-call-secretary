/**
 * UI module for the AI Call Secretary web interface.
 * Handles common UI elements and interactions.
 */

// Initialize UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Setup notification system
  setupNotifications();
  
  // Setup notification sound
  preloadNotificationSounds();
});

// Setup notifications
function setupNotifications() {
  // Create notifications container if it doesn't exist
  if (!document.querySelector('.notifications-container')) {
    const notificationsContainer = document.createElement('div');
    notificationsContainer.className = 'notifications-container';
    document.body.appendChild(notificationsContainer);
  }
}

// Show a notification
function showNotification(message, type = 'info', duration = 5000) {
  const container = document.querySelector('.notifications-container');
  if (!container) return;
  
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  
  // Add icon based on type
  let icon;
  switch (type) {
    case 'success':
      icon = 'fa-check-circle';
      break;
    case 'error':
      icon = 'fa-times-circle';
      break;
    case 'warning':
      icon = 'fa-exclamation-triangle';
      break;
    default:
      icon = 'fa-info-circle';
  }
  
  notification.innerHTML = `
    <div class="notification-icon">
      <i class="fas ${icon}"></i>
    </div>
    <div class="notification-content">
      <span class="notification-message">${message}</span>
    </div>
    <button class="notification-close">
      <i class="fas fa-times"></i>
    </button>
  `;
  
  // Add to container
  container.appendChild(notification);
  
  // Add close button event
  notification.querySelector('.notification-close').addEventListener('click', () => {
    notification.classList.add('fade-out');
    setTimeout(() => {
      notification.remove();
    }, 300);
  });
  
  // Show notification with animation
  setTimeout(() => {
    notification.classList.add('show');
  }, 10);
  
  // Auto-remove after duration
  if (duration > 0) {
    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.classList.add('fade-out');
        setTimeout(() => {
          notification.remove();
        }, 300);
      }
    }, duration);
  }
  
  return notification;
}

// Preload notification sounds
function preloadNotificationSounds() {
  const sounds = [
    { id: 'notification', path: 'assets/sounds/notification.mp3' },
    { id: 'call', path: 'assets/sounds/call.mp3' },
    { id: 'message', path: 'assets/sounds/message.mp3' },
    { id: 'appointment', path: 'assets/sounds/appointment.mp3' }
  ];
  
  // Create audio elements and preload
  sounds.forEach(sound => {
    try {
      const audio = new Audio();
      audio.id = `sound-${sound.id}`;
      audio.preload = 'auto';
      audio.src = sound.path;
      audio.load();
      
      // Add to DOM but keep hidden
      audio.style.display = 'none';
      document.body.appendChild(audio);
    } catch (error) {
      console.error(`Error preloading sound: ${sound.id}`, error);
    }
  });
}

// Play notification sound
function playNotificationSound(type = 'notification') {
  const audioId = `sound-${type}`;
  const audio = document.getElementById(audioId);
  
  if (audio) {
    // Reset and play
    audio.currentTime = 0;
    audio.play().catch(error => {
      console.error(`Error playing sound: ${type}`, error);
    });
  } else {
    // Fallback to creating audio on the fly
    try {
      const newAudio = new Audio(`assets/sounds/${type}.mp3`);
      newAudio.play().catch(error => {
        console.error(`Error playing sound: ${type}`, error);
      });
    } catch (error) {
      console.error(`Error creating sound: ${type}`, error);
    }
  }
}

// Create a WebSocket status indicator in the system status section
function createWebSocketStatusIndicator() {
  const systemStatus = document.getElementById('system-status');
  if (!systemStatus) return;
  
  // Check if WebSocket status item already exists
  if (systemStatus.querySelector('.status-item:contains("WebSocket")')) {
    return;
  }
  
  // Create new status item
  const statusItem = document.createElement('div');
  statusItem.className = 'status-item';
  statusItem.innerHTML = `
    <span class="status-label">WebSocket:</span>
    <span class="status-value">
      <span class="status-indicator offline"></span>
      Disconnected
    </span>
  `;
  
  // Add to system status
  systemStatus.appendChild(statusItem);
}

// Update the WebSocket status indicator
function updateWebSocketStatus(status, message = '') {
  const systemStatus = document.getElementById('system-status');
  if (!systemStatus) return;
  
  let statusItem = systemStatus.querySelector('.status-item:contains("WebSocket")');
  
  // Create status item if it doesn't exist
  if (!statusItem) {
    createWebSocketStatusIndicator();
    statusItem = systemStatus.querySelector('.status-item:contains("WebSocket")');
  }
  
  if (!statusItem) return;
  
  const statusIndicator = statusItem.querySelector('.status-indicator');
  const statusValue = statusItem.querySelector('.status-value');
  
  // Update based on status
  switch (status) {
    case 'connected':
    case 'authenticated':
      statusIndicator.className = 'status-indicator online';
      statusValue.textContent = 'Connected';
      break;
    case 'connecting':
      statusIndicator.className = 'status-indicator warning';
      statusValue.textContent = 'Connecting...';
      break;
    case 'disconnected':
      statusIndicator.className = 'status-indicator offline';
      statusValue.textContent = 'Disconnected';
      break;
    case 'error':
      statusIndicator.className = 'status-indicator error';
      statusValue.textContent = message || 'Error';
      break;
    case 'reconnecting':
      statusIndicator.className = 'status-indicator warning';
      statusValue.textContent = message || 'Reconnecting...';
      break;
    default:
      statusIndicator.className = 'status-indicator offline';
      statusValue.textContent = status;
  }
}

// Show a confirmation dialog
function showConfirmDialog(message, confirmCallback, cancelCallback = null) {
  // Create modal if it doesn't exist
  let modal = document.getElementById('confirm-dialog-modal');
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'confirm-dialog-modal';
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Confirm Action</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <p class="confirm-message"></p>
        </div>
        <div class="modal-footer">
          <button class="secondary-btn cancel-btn">Cancel</button>
          <button class="primary-btn confirm-btn">Confirm</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add close button event
    modal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal('confirm-dialog-modal');
      if (cancelCallback) cancelCallback();
    });
  }
  
  // Set message
  modal.querySelector('.confirm-message').textContent = message;
  
  // Set button events
  const confirmBtn = modal.querySelector('.confirm-btn');
  const cancelBtn = modal.querySelector('.cancel-btn');
  
  // Remove existing event listeners
  const newConfirmBtn = confirmBtn.cloneNode(true);
  const newCancelBtn = cancelBtn.cloneNode(true);
  
  confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
  cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
  
  // Add new event listeners
  newConfirmBtn.addEventListener('click', () => {
    closeModal('confirm-dialog-modal');
    if (confirmCallback) confirmCallback();
  });
  
  newCancelBtn.addEventListener('click', () => {
    closeModal('confirm-dialog-modal');
    if (cancelCallback) cancelCallback();
  });
  
  // Show modal
  openModal('confirm-dialog-modal');
}

// Show loading indicator
function showLoading(message = 'Loading...') {
  // Create loading element if it doesn't exist
  let loading = document.querySelector('.loading-overlay');
  
  if (!loading) {
    loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.innerHTML = `
      <div class="loading-spinner"></div>
      <div class="loading-message">${message}</div>
    `;
    
    document.body.appendChild(loading);
  } else {
    loading.querySelector('.loading-message').textContent = message;
  }
  
  // Show loading
  setTimeout(() => {
    loading.classList.add('show');
  }, 10);
  
  return loading;
}

// Hide loading indicator
function hideLoading() {
  const loading = document.querySelector('.loading-overlay');
  
  if (loading) {
    loading.classList.remove('show');
    setTimeout(() => {
      loading.remove();
    }, 300);
  }
}

// Format date with options
function formatDateWithOptions(dateString, options = {}) {
  const defaultOptions = { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  };
  
  const mergedOptions = { ...defaultOptions, ...options };
  return new Date(dateString).toLocaleString(undefined, mergedOptions);
}

// Format file size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Truncate text with ellipsis
function truncateText(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
}