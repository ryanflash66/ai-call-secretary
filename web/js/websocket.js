/**
 * WebSocket client for the AI Call Secretary web interface.
 * Handles real-time updates from the server.
 */

// WebSocket client class
class WebSocketClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000; // Initial reconnect delay (3 seconds)
    this.eventHandlers = {
      call: [],
      message: [],
      appointment: [],
      system: []
    };
    this.connected = false;
    this.authorized = false;
  }

  // Connect to WebSocket server
  connect() {
    try {
      // Check if WebSocket is supported
      if (!window.WebSocket) {
        console.error('WebSocket is not supported by this browser.');
        showNotification('Real-time updates are not supported by your browser.', 'warning');
        return false;
      }

      // Close existing connection if any
      if (this.socket) {
        this.socket.close();
      }

      // Extract WebSocket URL from API base URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const apiUrl = new URL(this.baseUrl);
      const wsUrl = `${wsProtocol}//${apiUrl.host}/ws`;

      // Create new WebSocket
      this.socket = new WebSocket(wsUrl);

      // Setup event handlers
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);

      return true;
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      return false;
    }
  }

  // Authenticate with WebSocket server
  authenticate() {
    if (!this.connected || !AUTH_TOKEN) return;

    this.sendMessage({
      type: 'auth',
      token: AUTH_TOKEN
    });
  }

  // Handle WebSocket open
  handleOpen(event) {
    console.log('WebSocket connection established');
    this.connected = true;
    this.reconnectAttempts = 0;
    this.reconnectDelay = 3000;
    this.authenticate();
    
    // Notify listeners of system status change
    this.triggerEvent('system', { status: 'connected' });
  }

  // Handle WebSocket close
  handleClose(event) {
    this.connected = false;
    this.authorized = false;
    console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
    
    // Notify listeners of system status change
    this.triggerEvent('system', { status: 'disconnected' });
    
    // Attempt to reconnect if not a normal closure
    if (event.code !== 1000) {
      this.reconnect();
    }
  }

  // Handle WebSocket error
  handleError(event) {
    console.error('WebSocket error:', event);
    
    // Notify listeners of system status change
    this.triggerEvent('system', { status: 'error', error: 'Connection error' });
  }

  // Handle WebSocket message
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      // Handle authentication response
      if (data.type === 'auth_response') {
        this.handleAuthResponse(data);
        return;
      }
      
      // Handle different event types
      if (data.type && this.eventHandlers[data.type]) {
        this.triggerEvent(data.type, data.data);
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
    }
  }

  // Handle authentication response
  handleAuthResponse(data) {
    if (data.status === 'success') {
      this.authorized = true;
      console.log('WebSocket authentication successful');
      
      // Notify listeners of system status change
      this.triggerEvent('system', { status: 'authenticated' });
    } else {
      this.authorized = false;
      console.error('WebSocket authentication failed:', data.message);
      
      // Notify listeners of system status change
      this.triggerEvent('system', { status: 'auth_failed', error: data.message });
      
      // Close connection if authentication failed
      this.socket.close();
    }
  }

  // Reconnect to WebSocket server
  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Maximum reconnect attempts reached. Giving up.');
      
      // Notify listeners of system status change
      this.triggerEvent('system', { 
        status: 'reconnect_failed', 
        error: 'Maximum reconnect attempts reached'
      });
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay / 1000} seconds... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    // Notify listeners of reconnect attempt
    this.triggerEvent('system', { 
      status: 'reconnecting',
      attempt: this.reconnectAttempts,
      maxAttempts: this.maxReconnectAttempts,
      delay: delay
    });
    
    setTimeout(() => {
      if (!this.connected) {
        this.connect();
      }
    }, delay);
  }

  // Send message to WebSocket server
  sendMessage(message) {
    if (!this.connected) {
      console.error('Cannot send message: WebSocket is not connected');
      return false;
    }
    
    try {
      this.socket.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  // Close WebSocket connection
  close() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    this.connected = false;
    this.authorized = false;
  }

  // Subscribe to events
  on(eventType, callback) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType].push(callback);
      return true;
    }
    
    return false;
  }

  // Unsubscribe from events
  off(eventType, callback) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(
        handler => handler !== callback
      );
      return true;
    }
    
    return false;
  }

  // Trigger event handlers
  triggerEvent(eventType, data) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType].forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in ${eventType} event handler:`, error);
        }
      });
    }
  }

  // Check if connected
  isConnected() {
    return this.connected;
  }

  // Check if authenticated
  isAuthenticated() {
    return this.connected && this.authorized;
  }
}

// Create global WebSocket client instance
const wsClient = new WebSocketClient(API_BASE_URL);

// Initialize WebSocket
function initWebSocket() {
  // Connect to WebSocket server
  const connected = wsClient.connect();
  
  if (connected) {
    // Setup event handlers
    setupWebSocketEvents();
  }
}

// Setup WebSocket event handlers
function setupWebSocketEvents() {
  // System events
  wsClient.on('system', handleSystemEvent);
  
  // Call events
  wsClient.on('call', handleCallEvent);
  
  // Message events
  wsClient.on('message', handleMessageEvent);
  
  // Appointment events
  wsClient.on('appointment', handleAppointmentEvent);
}

// Handle system events
function handleSystemEvent(data) {
  switch (data.status) {
    case 'connected':
      updateConnectionStatus('connected');
      break;
    case 'disconnected':
      updateConnectionStatus('disconnected');
      break;
    case 'error':
      updateConnectionStatus('error', data.error);
      break;
    case 'authenticated':
      updateConnectionStatus('authenticated');
      break;
    case 'auth_failed':
      updateConnectionStatus('auth_failed', data.error);
      break;
    case 'reconnecting':
      updateConnectionStatus('reconnecting', `Attempt ${data.attempt}/${data.maxAttempts}`);
      break;
    case 'reconnect_failed':
      updateConnectionStatus('reconnect_failed', data.error);
      break;
  }
}

// Update connection status in UI
function updateConnectionStatus(status, message = '') {
  // Update system status indicators if on dashboard
  const systemStatus = document.querySelector('#system-status');
  if (systemStatus) {
    const wsStatusItem = systemStatus.querySelector('.status-item:contains("WebSocket")');
    
    if (!wsStatusItem) {
      // Create WebSocket status item if it doesn't exist
      const newStatusItem = document.createElement('div');
      newStatusItem.className = 'status-item';
      newStatusItem.innerHTML = `
        <span class="status-label">WebSocket:</span>
        <span class="status-value">
          <span class="status-indicator offline"></span>
          Checking...
        </span>
      `;
      systemStatus.appendChild(newStatusItem);
    }
    
    // Update existing status item
    const wsStatusValue = wsStatusItem.querySelector('.status-value');
    const wsStatusIndicator = wsStatusItem.querySelector('.status-indicator');
    
    switch (status) {
      case 'connected':
      case 'authenticated':
        wsStatusIndicator.className = 'status-indicator online';
        wsStatusValue.textContent = 'Connected';
        break;
      case 'disconnected':
      case 'auth_failed':
      case 'reconnect_failed':
        wsStatusIndicator.className = 'status-indicator offline';
        wsStatusValue.textContent = message || 'Disconnected';
        break;
      case 'error':
        wsStatusIndicator.className = 'status-indicator error';
        wsStatusValue.textContent = message || 'Error';
        break;
      case 'reconnecting':
        wsStatusIndicator.className = 'status-indicator warning';
        wsStatusValue.textContent = message || 'Reconnecting...';
        break;
    }
  }
}

// Handle call events
function handleCallEvent(data) {
  switch (data.action) {
    case 'new':
      handleNewCall(data.call);
      break;
    case 'update':
      handleCallUpdate(data.call);
      break;
    case 'end':
      handleCallEnd(data.call_id);
      break;
  }
  
  // Refresh calls page if it's active
  if (currentPage === 'calls') {
    loadCalls();
  }
  
  // Refresh dashboard if it's active
  if (currentPage === 'dashboard') {
    loadRecentCalls();
  }
}

// Handle new call
function handleNewCall(call) {
  // Show notification
  showNotification(`New call from ${call.caller_name || call.caller_number || 'Unknown'}`, 'info');
  
  // Play notification sound
  playNotificationSound('call');
}

// Handle call update
function handleCallUpdate(call) {
  // If we're viewing the call details, update the view
  const callDetailModal = document.getElementById('call-detail-modal');
  if (callDetailModal && callDetailModal.classList.contains('active')) {
    const callIdElement = callDetailModal.querySelector('[data-call-id]');
    if (callIdElement && callIdElement.getAttribute('data-call-id') === call.call_id) {
      viewCall(call.call_id);
    }
  }
}

// Handle call end
function handleCallEnd(callId) {
  // Show notification
  showNotification('Call ended', 'info');
}

// Handle message events
function handleMessageEvent(data) {
  switch (data.action) {
    case 'new':
      handleNewMessage(data.message);
      break;
    case 'update':
      handleMessageUpdate(data.message);
      break;
  }
  
  // Refresh messages page if it's active
  if (currentPage === 'messages') {
    loadMessages();
  }
  
  // Refresh dashboard if it's active
  if (currentPage === 'dashboard') {
    loadRecentMessages();
  }
}

// Handle new message
function handleNewMessage(message) {
  // Show notification
  showNotification(`New message: ${message.subject || 'No subject'}`, 
    message.urgency === 'critical' ? 'error' : 
    message.urgency === 'high' ? 'warning' : 'info'
  );
  
  // Play notification sound
  playNotificationSound('message');
  
  // Increment notification badge
  incrementNotificationBadge();
}

// Handle message update
function handleMessageUpdate(message) {
  // If we're viewing the message details, update the view
  const messageDetailModal = document.getElementById('message-detail-modal');
  if (messageDetailModal && messageDetailModal.classList.contains('active')) {
    const messageIdElement = messageDetailModal.querySelector('[data-message-id]');
    if (messageIdElement && messageIdElement.getAttribute('data-message-id') === message.message_id) {
      viewMessage(message.message_id);
    }
  }
}

// Handle appointment events
function handleAppointmentEvent(data) {
  switch (data.action) {
    case 'new':
      handleNewAppointment(data.appointment);
      break;
    case 'update':
      handleAppointmentUpdate(data.appointment);
      break;
    case 'delete':
      handleAppointmentDelete(data.appointment_id);
      break;
  }
  
  // Refresh appointments page if it's active
  if (currentPage === 'appointments') {
    loadAppointments();
  }
  
  // Refresh dashboard if it's active
  if (currentPage === 'dashboard') {
    loadUpcomingAppointments();
  }
}

// Handle new appointment
function handleNewAppointment(appointment) {
  // Show notification
  showNotification(`New appointment: ${appointment.title}`, 'info');
  
  // Play notification sound
  playNotificationSound('appointment');
  
  // Increment notification badge
  incrementNotificationBadge();
}

// Handle appointment update
function handleAppointmentUpdate(appointment) {
  // If we're viewing the appointment details, update the view
  const appointmentDetailModal = document.getElementById('appointment-detail-modal');
  if (appointmentDetailModal && appointmentDetailModal.classList.contains('active')) {
    const appointmentIdElement = appointmentDetailModal.querySelector('[data-appointment-id]');
    if (appointmentIdElement && appointmentIdElement.getAttribute('data-appointment-id') === appointment.appointment_id) {
      viewAppointment(appointment.appointment_id);
    }
  }
}

// Handle appointment delete
function handleAppointmentDelete(appointmentId) {
  // If we're viewing the deleted appointment, close the modal
  const appointmentDetailModal = document.getElementById('appointment-detail-modal');
  if (appointmentDetailModal && appointmentDetailModal.classList.contains('active')) {
    const appointmentIdElement = appointmentDetailModal.querySelector('[data-appointment-id]');
    if (appointmentIdElement && appointmentIdElement.getAttribute('data-appointment-id') === appointmentId) {
      closeModal('appointment-detail-modal');
    }
  }
}

// Play notification sound
function playNotificationSound(type) {
  // Create audio element
  const audio = document.createElement('audio');
  
  // Set source based on notification type
  switch (type) {
    case 'call':
      audio.src = 'assets/sounds/call.mp3';
      break;
    case 'message':
      audio.src = 'assets/sounds/message.mp3';
      break;
    case 'appointment':
      audio.src = 'assets/sounds/appointment.mp3';
      break;
    default:
      audio.src = 'assets/sounds/notification.mp3';
  }
  
  // Play sound
  audio.play().catch(error => {
    console.error('Error playing notification sound:', error);
  });
}

// Increment notification badge
function incrementNotificationBadge() {
  const badge = document.querySelector('.notification-badge');
  if (badge) {
    const count = parseInt(badge.textContent) || 0;
    badge.textContent = count + 1;
    badge.style.display = 'block';
  }
}