/**
 * Calls module for the AI Call Secretary web interface.
 * Handles the calls page functionality.
 */

// Global state for calls page
const callsState = {
  page: 1,
  pageSize: 10,
  total: 0,
  status: 'all',
  date: '',
  calls: []
};

// Initialize calls page
function initCallsPage() {
  // Set up event listeners
  setupCallsFilters();
  setupCallsRefresh();
  setupCallsPagination();
  
  // Load calls
  loadCalls();
}

// Set up calls filters
function setupCallsFilters() {
  // Status filter
  const statusFilter = document.getElementById('call-status-filter');
  statusFilter.addEventListener('change', () => {
    callsState.status = statusFilter.value;
    callsState.page = 1;
    loadCalls();
  });
  
  // Date filter
  const dateFilter = document.getElementById('call-date-filter');
  dateFilter.addEventListener('change', () => {
    callsState.date = dateFilter.value;
    callsState.page = 1;
    loadCalls();
  });
  
  // Reset filters
  const resetBtn = document.querySelector('.filter-reset-btn');
  resetBtn.addEventListener('click', () => {
    statusFilter.value = 'all';
    dateFilter.value = '';
    callsState.status = 'all';
    callsState.date = '';
    callsState.page = 1;
    loadCalls();
  });
}

// Set up calls refresh
function setupCallsRefresh() {
  const refreshBtn = document.querySelector('.calls-container .refresh-btn');
  refreshBtn.addEventListener('click', () => {
    loadCalls();
  });
}

// Set up calls pagination
function setupCallsPagination() {
  const prevBtn = document.querySelector('.calls-container .pagination-btn:first-child');
  const nextBtn = document.querySelector('.calls-container .pagination-btn:last-child');
  
  prevBtn.addEventListener('click', () => {
    if (callsState.page > 1) {
      callsState.page--;
      loadCalls();
    }
  });
  
  nextBtn.addEventListener('click', () => {
    const maxPage = Math.ceil(callsState.total / callsState.pageSize);
    if (callsState.page < maxPage) {
      callsState.page++;
      loadCalls();
    }
  });
}

// Load calls
function loadCalls() {
  // Build filters
  const filters = {
    page: callsState.page,
    page_size: callsState.pageSize
  };
  
  if (callsState.status !== 'all') {
    filters.status = callsState.status;
  }
  
  if (callsState.date) {
    filters.start_date = `${callsState.date}T00:00:00`;
    filters.end_date = `${callsState.date}T23:59:59`;
  }
  
  // Show loading state
  const tableBody = document.getElementById('calls-table');
  tableBody.innerHTML = `
    <tr class="placeholder-row">
      <td colspan="6" class="text-center">Loading calls...</td>
    </tr>
  `;
  
  // Fetch calls
  api.getCalls(filters)
    .then(data => {
      callsState.calls = data.calls;
      callsState.total = data.total;
      
      // Update pagination info
      updateCallsPagination();
      
      // Render calls
      renderCalls();
    })
    .catch(error => {
      console.error('Error loading calls:', error);
      tableBody.innerHTML = `
        <tr class="placeholder-row">
          <td colspan="6" class="text-center">Error loading calls</td>
        </tr>
      `;
    });
}

// Update calls pagination
function updateCallsPagination() {
  const paginationInfo = document.querySelector('.calls-container .pagination-info');
  const prevBtn = document.querySelector('.calls-container .pagination-btn:first-child');
  const nextBtn = document.querySelector('.calls-container .pagination-btn:last-child');
  
  const maxPage = Math.ceil(callsState.total / callsState.pageSize) || 1;
  
  paginationInfo.textContent = `Page ${callsState.page} of ${maxPage}`;
  
  prevBtn.disabled = callsState.page <= 1;
  nextBtn.disabled = callsState.page >= maxPage;
}

// Render calls
function renderCalls() {
  const tableBody = document.getElementById('calls-table');
  
  if (callsState.calls.length === 0) {
    tableBody.innerHTML = `
      <tr class="placeholder-row">
        <td colspan="6" class="text-center">No calls found</td>
      </tr>
    `;
    return;
  }
  
  tableBody.innerHTML = '';
  
  callsState.calls.forEach(call => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${call.caller_name || 'Unknown'}</td>
      <td>${call.caller_number || 'Unknown'}</td>
      <td>${formatDateTime(call.start_time)}</td>
      <td>${formatDuration(call.duration)}</td>
      <td><span class="status-badge ${call.status}">${call.status}</span></td>
      <td>
        <button class="action-btn view-call-btn" data-call-id="${call.call_id}">
          <i class="fas fa-eye"></i>
        </button>
        <button class="action-btn delete-call-btn" data-call-id="${call.call_id}">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    `;
    
    tableBody.appendChild(row);
  });
  
  // Add event listeners for call actions
  setupCallActions();
}

// Set up call actions
function setupCallActions() {
  // View call
  document.querySelectorAll('.view-call-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const callId = btn.getAttribute('data-call-id');
      viewCall(callId);
    });
  });
  
  // Delete call
  document.querySelectorAll('.delete-call-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const callId = btn.getAttribute('data-call-id');
      deleteCall(callId);
    });
  });
}

// View call details
function viewCall(callId) {
  api.getCall(callId)
    .then(call => {
      // Populate modal with call details
      const modalBody = document.querySelector('#call-detail-modal .modal-body');
      
      modalBody.innerHTML = `
        <div class="call-details">
          <div class="detail-group">
            <span class="detail-label">Caller:</span>
            <span class="detail-value">${call.caller_name || 'Unknown'}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Number:</span>
            <span class="detail-value">${call.caller_number || 'Unknown'}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Time:</span>
            <span class="detail-value">${formatDateTime(call.start_time)}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Duration:</span>
            <span class="detail-value">${formatDuration(call.duration)}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Status:</span>
            <span class="detail-value"><span class="status-badge ${call.status}">${call.status}</span></span>
          </div>
        </div>
        
        <div class="call-transcript">
          <h4>Transcript</h4>
          <div class="transcript-container">
            ${call.transcript ? renderTranscript(call.transcript.items) : '<p class="placeholder-text">No transcript available</p>'}
          </div>
        </div>
        
        <div class="call-actions">
          <h4>Actions Performed</h4>
          <div class="actions-container">
            ${call.actions.length > 0 ? renderActions(call.actions) : '<p class="placeholder-text">No actions performed</p>'}
          </div>
        </div>
      `;
      
      // Show modal
      openModal('call-detail-modal');
    })
    .catch(error => {
      console.error('Error loading call details:', error);
      showNotification('Error loading call details', 'error');
    });
}

// Render transcript
function renderTranscript(items) {
  if (!items || items.length === 0) {
    return '<p class="placeholder-text">No transcript available</p>';
  }
  
  let html = '<div class="transcript-messages">';
  
  items.forEach(item => {
    html += `
      <div class="transcript-message ${item.speaker}">
        <div class="message-speaker">${item.speaker === 'user' ? 'Caller' : 'AI Secretary'}</div>
        <div class="message-text">${item.text}</div>
        <div class="message-time">${formatTime(item.timestamp)}</div>
      </div>
    `;
  });
  
  html += '</div>';
  
  return html;
}

// Render actions
function renderActions(actions) {
  if (!actions || actions.length === 0) {
    return '<p class="placeholder-text">No actions performed</p>';
  }
  
  let html = '<div class="action-list">';
  
  actions.forEach(action => {
    html += `
      <div class="action-item ${action.success ? 'success' : 'error'}">
        <div class="action-header">
          <span class="action-type">${action.action_type.replace(/_/g, ' ')}</span>
          <span class="action-status">${action.success ? 'Success' : 'Failed'}</span>
        </div>
        <div class="action-details">
          ${renderActionDetails(action)}
        </div>
        <div class="action-time">${formatTime(action.timestamp)}</div>
      </div>
    `;
  });
  
  html += '</div>';
  
  return html;
}

// Render action details
function renderActionDetails(action) {
  if (!action.details) {
    return '';
  }
  
  let html = '<ul class="action-params">';
  
  Object.entries(action.details).forEach(([key, value]) => {
    if (key !== 'success' && key !== 'message') {
      html += `<li><span class="param-name">${key}:</span> <span class="param-value">${value}</span></li>`;
    }
  });
  
  html += '</ul>';
  
  if (action.details.message) {
    html += `<div class="action-message">${action.details.message}</div>`;
  }
  
  return html;
}

// Delete call
function deleteCall(callId) {
  if (confirm('Are you sure you want to delete this call?')) {
    api.deleteCall(callId)
      .then(() => {
        showNotification('Call deleted successfully', 'success');
        loadCalls();
      })
      .catch(error => {
        console.error('Error deleting call:', error);
        showNotification('Error deleting call', 'error');
      });
  }
}