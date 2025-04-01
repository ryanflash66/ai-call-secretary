/**
 * Dashboard module for the AI Call Secretary web interface.
 * Handles the dashboard page functionality.
 */

// Initialize dashboard
function initDashboard() {
  loadDashboardStats();
  loadRecentCalls();
  loadRecentMessages();
  loadUpcomingAppointments();
  loadSystemStatus();
  
  // Create WebSocket status indicator
  if (typeof createWebSocketStatusIndicator === 'function') {
    createWebSocketStatusIndicator();
  }
  
  // Setup real-time updates display
  setupRealtimeUpdates();
  
  // Create chart containers
  createChartContainers();
  
  // Initialize charts if available
  if (typeof initDashboardCharts === 'function') {
    setTimeout(() => {
      initDashboardCharts();
    }, 500); // Small delay to ensure containers are rendered
  }
}

// Load dashboard statistics
function loadDashboardStats() {
  Promise.all([
    api.getCalls({ page: 1, page_size: 1 }),
    api.get('/messages', { page: 1, page_size: 1 }),
    api.get('/appointments', { page: 1, page_size: 1 })
  ])
  .then(([callsData, messagesData, appointmentsData]) => {
    // Update statistics
    updateStatCard('Total Calls', callsData.total);
    updateStatCard('Messages', messagesData.total);
    updateStatCard('Appointments', appointmentsData.total);
    
    // Calculate unique callers
    api.get('/calls/unique-callers')
      .then(data => {
        updateStatCard('Unique Callers', data.count);
      })
      .catch(error => {
        console.error('Error loading unique callers:', error);
        updateStatCard('Unique Callers', 0);
      });
  })
  .catch(error => {
    console.error('Error loading dashboard stats:', error);
    // Set default values in case of error
    updateStatCard('Total Calls', 0);
    updateStatCard('Messages', 0);
    updateStatCard('Appointments', 0);
    updateStatCard('Unique Callers', 0);
  });
}

// Update a stat card with value
function updateStatCard(title, value) {
  const statCards = document.querySelectorAll('.stat-card');
  
  for (const card of statCards) {
    const titleElement = card.querySelector('h3');
    if (titleElement && titleElement.textContent === title) {
      const valueElement = card.querySelector('.stat-value');
      if (valueElement) {
        valueElement.textContent = value;
      }
      break;
    }
  }
}

// Load recent calls
function loadRecentCalls() {
  api.getCalls({ page: 1, page_size: 5 })
    .then(data => {
      const tableBody = document.getElementById('recent-calls-table');
      
      if (data.calls.length === 0) {
        tableBody.innerHTML = `
          <tr class="placeholder-row">
            <td colspan="4" class="text-center">No recent calls</td>
          </tr>
        `;
        return;
      }
      
      tableBody.innerHTML = '';
      
      data.calls.forEach(call => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${call.caller_name || 'Unknown'}</td>
          <td>${formatDateTime(call.start_time)}</td>
          <td>${formatDuration(call.duration)}</td>
          <td><span class="status-badge ${call.status}">${call.status}</span></td>
        `;
        
        tableBody.appendChild(row);
      });
    })
    .catch(error => {
      console.error('Error loading recent calls:', error);
      const tableBody = document.getElementById('recent-calls-table');
      tableBody.innerHTML = `
        <tr class="placeholder-row">
          <td colspan="4" class="text-center">Error loading calls</td>
        </tr>
      `;
    });
}

// Load recent messages
function loadRecentMessages() {
  api.get('/messages', { page: 1, page_size: 3 })
    .then(data => {
      const messageList = document.getElementById('recent-messages');
      
      if (data.messages.length === 0) {
        messageList.innerHTML = `<p class="placeholder-text">No recent messages</p>`;
        return;
      }
      
      messageList.innerHTML = '';
      
      data.messages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.className = `message-item ${message.urgency}`;
        messageElement.innerHTML = `
          <div class="message-header">
            <span class="message-from">${message.caller_name || 'Unknown'}</span>
            <span class="message-time">${formatDate(message.timestamp)}</span>
          </div>
          <div class="message-content">${message.message}</div>
          <div class="message-footer">
            <span class="message-urgency ${message.urgency}">${message.urgency}</span>
            ${message.callback_requested ? '<span class="callback-badge">Callback Requested</span>' : ''}
          </div>
        `;
        
        messageList.appendChild(messageElement);
      });
    })
    .catch(error => {
      console.error('Error loading recent messages:', error);
      const messageList = document.getElementById('recent-messages');
      messageList.innerHTML = `<p class="placeholder-text">Error loading messages</p>`;
    });
}

// Load upcoming appointments
function loadUpcomingAppointments() {
  api.get('/appointments', { page: 1, page_size: 3, status: 'scheduled' })
    .then(data => {
      const appointmentList = document.getElementById('upcoming-appointments');
      
      if (data.appointments.length === 0) {
        appointmentList.innerHTML = `<p class="placeholder-text">No upcoming appointments</p>`;
        return;
      }
      
      appointmentList.innerHTML = '';
      
      data.appointments.forEach(appointment => {
        const appointmentElement = document.createElement('div');
        appointmentElement.className = 'appointment-item';
        appointmentElement.innerHTML = `
          <div class="appointment-header">
            <span class="appointment-title">${appointment.name}</span>
            <span class="appointment-date">${formatDate(appointment.date)}</span>
          </div>
          <div class="appointment-details">
            <div class="appointment-time">
              <i class="fas fa-clock"></i> ${appointment.time} (${appointment.duration} min)
            </div>
            ${appointment.purpose ? `<div class="appointment-purpose">${appointment.purpose}</div>` : ''}
          </div>
        `;
        
        appointmentList.appendChild(appointmentElement);
      });
    })
    .catch(error => {
      console.error('Error loading upcoming appointments:', error);
      const appointmentList = document.getElementById('upcoming-appointments');
      appointmentList.innerHTML = `<p class="placeholder-text">Error loading appointments</p>`;
    });
}

// Load system status
function loadSystemStatus() {
  api.getSystemStatus()
    .then(data => {
      systemStatus = data;
      updateSystemStatusUI();
    })
    .catch(error => {
      console.error('Error loading system status:', error);
    });
}

// Setup real-time updates display
function setupRealtimeUpdates() {
  // Create or get real-time updates container
  let realtimeContainer = document.getElementById('realtime-updates');
  
  if (!realtimeContainer) {
    // Create a new card for real-time updates
    const dashboardGrid = document.querySelector('.dashboard-grid');
    if (!dashboardGrid) return;
    
    const realtimeCard = document.createElement('div');
    realtimeCard.className = 'dashboard-card realtime-card';
    realtimeCard.innerHTML = `
      <div class="card-header">
        <h3>Real-time Updates</h3>
        <button class="clear-btn"><i class="fas fa-trash"></i> Clear</button>
      </div>
      <div class="card-content">
        <div id="realtime-updates" class="realtime-updates">
          <p class="placeholder-text">No recent updates</p>
        </div>
      </div>
    `;
    
    dashboardGrid.appendChild(realtimeCard);
    
    // Get the container
    realtimeContainer = document.getElementById('realtime-updates');
    
    // Add clear button functionality
    realtimeCard.querySelector('.clear-btn').addEventListener('click', () => {
      realtimeContainer.innerHTML = `<p class="placeholder-text">No recent updates</p>`;
    });
  }
  
  // Set up WebSocket event listeners if websocket is available
  if (typeof wsClient !== 'undefined' && wsClient) {
    // Create event handler functions
    const handleCall = (data) => {
      addRealtimeUpdate('call', data);
    };
    
    const handleMessage = (data) => {
      addRealtimeUpdate('message', data);
    };
    
    const handleAppointment = (data) => {
      addRealtimeUpdate('appointment', data);
    };
    
    const handleSystem = (data) => {
      if (data.status === 'connected' || data.status === 'authenticated') {
        addRealtimeUpdate('system', { 
          action: 'connected',
          message: 'WebSocket connected' 
        });
      } else if (data.status === 'disconnected') {
        addRealtimeUpdate('system', { 
          action: 'disconnected',
          message: 'WebSocket disconnected' 
        });
      }
    };
    
    // Register event handlers
    wsClient.on('call', handleCall);
    wsClient.on('message', handleMessage);
    wsClient.on('appointment', handleAppointment);
    wsClient.on('system', handleSystem);
  }
}

// Create chart containers
function createChartContainers() {
  // Create charts section if it doesn't exist
  let chartsSection = document.querySelector('.charts-section');
  
  if (!chartsSection) {
    // Insert charts section before real-time updates
    const dashboardGrid = document.querySelector('.dashboard-grid');
    
    if (!dashboardGrid) return;
    
    chartsSection = document.createElement('div');
    chartsSection.className = 'charts-section';
    chartsSection.innerHTML = `
      <div class="charts-row">
        <div class="chart-card">
          <div class="card-header">
            <h3>Call Volume (Last 7 Days)</h3>
          </div>
          <div class="card-content">
            <div class="chart-container">
              <canvas id="call-volume-chart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="card-header">
            <h3>Call Duration by Hour</h3>
          </div>
          <div class="card-content">
            <div class="chart-container">
              <canvas id="call-duration-chart"></canvas>
            </div>
          </div>
        </div>
      </div>
      
      <div class="charts-row">
        <div class="chart-card">
          <div class="card-header">
            <h3>Message Distribution</h3>
          </div>
          <div class="card-content">
            <div class="chart-container">
              <canvas id="message-distribution-chart"></canvas>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="card-header">
            <h3>Appointments by Day</h3>
          </div>
          <div class="card-content">
            <div class="chart-container">
              <canvas id="appointment-schedule-chart"></canvas>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Insert before the first regular dashboard card
    dashboardGrid.insertBefore(chartsSection, dashboardGrid.firstChild);
  }
}

// Add a real-time update to the dashboard
function addRealtimeUpdate(type, data) {
  const container = document.getElementById('realtime-updates');
  if (!container) return;
  
  // Remove placeholder if present
  const placeholder = container.querySelector('.placeholder-text');
  if (placeholder) {
    placeholder.remove();
  }
  
  // Create update element
  const updateEl = document.createElement('div');
  updateEl.className = `realtime-update ${type}`;
  
  // Current time
  const now = new Date();
  const time = now.toLocaleTimeString();
  
  // Generate content based on type and action
  let content = '';
  let icon = '';
  
  switch (type) {
    case 'call':
      icon = 'fa-phone-alt';
      if (data.action === 'new') {
        content = `New call from ${data.call.caller_name || data.call.caller_number || 'Unknown'}`;
      } else if (data.action === 'update') {
        content = `Call ${data.call.call_id} updated`;
      } else if (data.action === 'end') {
        content = `Call ended`;
      }
      break;
      
    case 'message':
      icon = 'fa-envelope';
      if (data.action === 'new') {
        content = `New message: ${data.message.subject || 'No subject'}`;
      } else if (data.action === 'update') {
        content = `Message updated: ${data.message.subject || 'No subject'}`;
      }
      break;
      
    case 'appointment':
      icon = 'fa-calendar-alt';
      if (data.action === 'new') {
        content = `New appointment: ${data.appointment.title}`;
      } else if (data.action === 'update') {
        content = `Appointment updated: ${data.appointment.title}`;
      } else if (data.action === 'delete') {
        content = `Appointment deleted`;
      }
      break;
      
    case 'system':
      icon = 'fa-server';
      content = data.message || 'System update';
      break;
  }
  
  // Set content
  updateEl.innerHTML = `
    <div class="update-icon">
      <i class="fas ${icon}"></i>
    </div>
    <div class="update-content">
      <div class="update-message">${content}</div>
      <div class="update-time">${time}</div>
    </div>
  `;
  
  // Add to container (at the top)
  container.insertBefore(updateEl, container.firstChild);
  
  // Limit the number of updates (keep last 10)
  const updates = container.querySelectorAll('.realtime-update');
  if (updates.length > 10) {
    for (let i = 10; i < updates.length; i++) {
      updates[i].remove();
    }
  }
}