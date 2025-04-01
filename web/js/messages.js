/**
 * Messages module for the AI Call Secretary web interface.
 * Handles the messages page functionality.
 */

// Global state for messages page
const messagesState = {
  page: 1,
  pageSize: 10,
  total: 0,
  urgency: 'all',
  date: '',
  messages: []
};

// Initialize messages page
function initMessagesPage() {
  // Create message detail and form modals
  createMessageModals();
  
  // Set up event listeners
  setupMessagesFilters();
  setupMessagesRefresh();
  setupMessagesPagination();
  setupNewMessageButton();
  
  // Load messages
  loadMessages();
}

// Create message modals
function createMessageModals() {
  // Create message detail modal if it doesn't exist
  if (!document.getElementById('message-detail-modal')) {
    const detailModal = document.createElement('div');
    detailModal.id = 'message-detail-modal';
    detailModal.className = 'modal';
    detailModal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>Message Details</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <!-- Message details will be loaded here -->
        </div>
        <div class="modal-footer">
          <button class="secondary-btn close-modal-btn">Close</button>
          <button class="primary-btn reply-btn"><i class="fas fa-reply"></i> Reply</button>
        </div>
      </div>
    `;
    document.body.appendChild(detailModal);
    
    // Add event listeners
    detailModal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal('message-detail-modal');
    });
    
    detailModal.querySelector('.close-modal-btn').addEventListener('click', () => {
      closeModal('message-detail-modal');
    });
  }
  
  // Create message form modal if it doesn't exist
  if (!document.getElementById('message-form-modal')) {
    const formModal = document.createElement('div');
    formModal.id = 'message-form-modal';
    formModal.className = 'modal';
    formModal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>New Message</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <form id="message-form" class="message-form">
            <div class="form-group">
              <label for="message-recipient">To:</label>
              <input type="text" id="message-recipient" name="recipient" required>
            </div>
            <div class="form-group">
              <label for="message-subject">Subject:</label>
              <input type="text" id="message-subject" name="subject" required>
            </div>
            <div class="form-group">
              <label for="message-urgency">Urgency:</label>
              <select id="message-urgency" name="urgency" required>
                <option value="normal">Normal</option>
                <option value="low">Low</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div class="form-group">
              <label for="message-content">Message:</label>
              <textarea id="message-content" name="content" rows="8" required></textarea>
            </div>
            <div class="form-error" id="message-form-error"></div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="secondary-btn close-modal-btn">Cancel</button>
          <button class="primary-btn" id="send-message-btn">Send Message</button>
        </div>
      </div>
    `;
    document.body.appendChild(formModal);
    
    // Add event listeners
    formModal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal('message-form-modal');
    });
    
    formModal.querySelector('.close-modal-btn').addEventListener('click', () => {
      closeModal('message-form-modal');
    });
  }
}

// Set up messages filters
function setupMessagesFilters() {
  // Urgency filter
  const urgencyFilter = document.getElementById('message-urgency-filter');
  urgencyFilter.addEventListener('change', () => {
    messagesState.urgency = urgencyFilter.value;
    messagesState.page = 1;
    loadMessages();
  });
  
  // Date filter
  const dateFilter = document.getElementById('message-date-filter');
  dateFilter.addEventListener('change', () => {
    messagesState.date = dateFilter.value;
    messagesState.page = 1;
    loadMessages();
  });
  
  // Reset filters
  const resetBtn = document.querySelector('.messages-container').closest('.page').querySelector('.filter-reset-btn');
  resetBtn.addEventListener('click', () => {
    urgencyFilter.value = 'all';
    dateFilter.value = '';
    messagesState.urgency = 'all';
    messagesState.date = '';
    messagesState.page = 1;
    loadMessages();
  });
}

// Set up messages refresh
function setupMessagesRefresh() {
  const refreshBtn = document.querySelector('#messages .refresh-btn');
  refreshBtn.addEventListener('click', () => {
    loadMessages();
  });
}

// Set up messages pagination
function setupMessagesPagination() {
  const prevBtn = document.querySelector('#messages .pagination-btn:first-child');
  const nextBtn = document.querySelector('#messages .pagination-btn:last-child');
  
  prevBtn.addEventListener('click', () => {
    if (messagesState.page > 1) {
      messagesState.page--;
      loadMessages();
    }
  });
  
  nextBtn.addEventListener('click', () => {
    const maxPage = Math.ceil(messagesState.total / messagesState.pageSize);
    if (messagesState.page < maxPage) {
      messagesState.page++;
      loadMessages();
    }
  });
}

// Setup new message button
function setupNewMessageButton() {
  const newMessageBtn = document.getElementById('new-message-btn');
  newMessageBtn.addEventListener('click', () => {
    showNewMessageModal();
  });
}

// Load messages
function loadMessages() {
  // Build filters
  const filters = {
    page: messagesState.page,
    page_size: messagesState.pageSize
  };
  
  if (messagesState.urgency !== 'all') {
    filters.urgency = messagesState.urgency;
  }
  
  if (messagesState.date) {
    filters.start_date = `${messagesState.date}T00:00:00`;
    filters.end_date = `${messagesState.date}T23:59:59`;
  }
  
  // Show loading state
  const messagesList = document.getElementById('messages-list');
  messagesList.innerHTML = `
    <p class="placeholder-text">Loading messages...</p>
  `;
  
  // Fetch messages
  api.getMessages(filters)
    .then(data => {
      messagesState.messages = data.messages;
      messagesState.total = data.total;
      
      // Update pagination info
      updateMessagesPagination();
      
      // Render messages
      renderMessages();
    })
    .catch(error => {
      console.error('Error loading messages:', error);
      messagesList.innerHTML = `
        <p class="placeholder-text">Error loading messages</p>
      `;
    });
}

// Update messages pagination
function updateMessagesPagination() {
  const paginationInfo = document.querySelector('#messages .pagination-info');
  const prevBtn = document.querySelector('#messages .pagination-btn:first-child');
  const nextBtn = document.querySelector('#messages .pagination-btn:last-child');
  
  const maxPage = Math.ceil(messagesState.total / messagesState.pageSize) || 1;
  
  paginationInfo.textContent = `Page ${messagesState.page} of ${maxPage}`;
  
  prevBtn.disabled = messagesState.page <= 1;
  nextBtn.disabled = messagesState.page >= maxPage;
}

// Render messages
function renderMessages() {
  const messagesList = document.getElementById('messages-list');
  
  if (messagesState.messages.length === 0) {
    messagesList.innerHTML = `
      <p class="placeholder-text">No messages found</p>
    `;
    return;
  }
  
  messagesList.innerHTML = '';
  
  messagesState.messages.forEach(message => {
    const messageItem = document.createElement('div');
    messageItem.className = `message-item ${message.urgency}`;
    messageItem.innerHTML = `
      <div class="message-header">
        <div class="message-info">
          <span class="message-sender">${message.sender || 'System'}</span>
          <span class="message-time">${formatDateTime(message.timestamp)}</span>
        </div>
        <div class="message-actions">
          <button class="action-btn view-message-btn" data-message-id="${message.message_id}">
            <i class="fas fa-eye"></i>
          </button>
          <button class="action-btn reply-message-btn" data-message-id="${message.message_id}">
            <i class="fas fa-reply"></i>
          </button>
          <button class="action-btn delete-message-btn" data-message-id="${message.message_id}">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>
      <div class="message-preview">
        <span class="urgency-indicator ${message.urgency}">${message.urgency}</span>
        <p class="message-subject">${message.subject || 'No subject'}</p>
        <p class="message-content-preview">${message.content ? truncateText(message.content, 100) : 'No content'}</p>
      </div>
    `;
    
    messagesList.appendChild(messageItem);
  });
  
  // Add event listeners for message actions
  setupMessageActions();
}

// Helper function to truncate text
function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
}

// Set up message actions
function setupMessageActions() {
  // View message
  document.querySelectorAll('.view-message-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const messageId = btn.getAttribute('data-message-id');
      viewMessage(messageId);
    });
  });
  
  // Reply to message
  document.querySelectorAll('.reply-message-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const messageId = btn.getAttribute('data-message-id');
      replyToMessage(messageId);
    });
  });
  
  // Delete message
  document.querySelectorAll('.delete-message-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const messageId = btn.getAttribute('data-message-id');
      deleteMessage(messageId);
    });
  });
}

// View message details
function viewMessage(messageId) {
  api.getMessage(messageId)
    .then(message => {
      // Get the modal
      const modalId = 'message-detail-modal';
      const modal = document.getElementById(modalId);
      
      // Populate modal with message details
      const modalBody = modal.querySelector('.modal-body');
      
      modalBody.innerHTML = `
        <div class="message-details">
          <div class="detail-group">
            <span class="detail-label">From:</span>
            <span class="detail-value">${message.sender || 'System'}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Urgency:</span>
            <span class="detail-value"><span class="urgency-indicator ${message.urgency}">${message.urgency}</span></span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Time:</span>
            <span class="detail-value">${formatDateTime(message.timestamp)}</span>
          </div>
          <div class="detail-group">
            <span class="detail-label">Subject:</span>
            <span class="detail-value">${message.subject || 'No subject'}</span>
          </div>
        </div>
        
        <div class="message-content">
          <h4>Message</h4>
          <div class="content-container">
            ${message.content ? message.content.replace(/\n/g, '<br>') : '<p class="placeholder-text">No content</p>'}
          </div>
        </div>
        
        ${message.call_id ? `
          <div class="related-call">
            <h4>Related Call</h4>
            <button class="secondary-btn view-related-call-btn" data-call-id="${message.call_id}">
              <i class="fas fa-phone-alt"></i> View Call Details
            </button>
          </div>
        ` : ''}
      `;
      
      // Add event listener for related call button if it exists
      const relatedCallBtn = modalBody.querySelector('.view-related-call-btn');
      if (relatedCallBtn) {
        relatedCallBtn.addEventListener('click', () => {
          closeModal(modalId);
          viewCall(message.call_id);
        });
      }
      
      // Update reply button event listener
      const replyBtn = modal.querySelector('.reply-btn');
      if (replyBtn) {
        // Remove existing event listeners
        const newReplyBtn = replyBtn.cloneNode(true);
        replyBtn.parentNode.replaceChild(newReplyBtn, replyBtn);
        
        // Add new event listener
        newReplyBtn.addEventListener('click', () => {
          closeModal(modalId);
          replyToMessage(messageId);
        });
      }
      
      // Show modal
      openModal(modalId);
    })
    .catch(error => {
      console.error('Error loading message details:', error);
      showNotification('Error loading message details', 'error');
    });
}

// Reply to message
function replyToMessage(messageId) {
  // Get the original message first
  api.getMessage(messageId)
    .then(message => {
      showMessageForm({
        isReply: true,
        originalMessage: message,
        subject: `Re: ${message.subject || 'No subject'}`,
        recipient: message.sender,
        content: `\n\n--- Original message from ${message.sender} on ${formatDateTime(message.timestamp)} ---\n${message.content}`
      });
    })
    .catch(error => {
      console.error('Error loading original message:', error);
      showNotification('Error preparing reply', 'error');
    });
}

// Show new message modal
function showNewMessageModal() {
  showMessageForm({
    isReply: false,
    subject: '',
    recipient: '',
    content: ''
  });
}

// Show message form (new or reply)
function showMessageForm(options) {
  const modalId = 'message-form-modal';
  
  // Check if modal already exists
  let modal = document.getElementById(modalId);
  
  // Create modal if it doesn't exist
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h3>${options.isReply ? 'Reply to Message' : 'New Message'}</h3>
          <button class="close-btn"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
          <form id="message-form" class="message-form">
            <div class="form-group">
              <label for="message-recipient">To:</label>
              <input type="text" id="message-recipient" name="recipient" required value="${options.recipient || ''}">
            </div>
            <div class="form-group">
              <label for="message-subject">Subject:</label>
              <input type="text" id="message-subject" name="subject" required value="${options.subject || ''}">
            </div>
            <div class="form-group">
              <label for="message-urgency">Urgency:</label>
              <select id="message-urgency" name="urgency" required>
                <option value="normal">Normal</option>
                <option value="low">Low</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div class="form-group">
              <label for="message-content">Message:</label>
              <textarea id="message-content" name="content" rows="8" required>${options.content || ''}</textarea>
            </div>
            <div class="form-error" id="message-form-error"></div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="secondary-btn close-modal-btn">Cancel</button>
          <button class="primary-btn" id="send-message-btn">Send Message</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    modal.querySelector('.close-btn').addEventListener('click', () => {
      closeModal(modalId);
    });
    
    modal.querySelector('.close-modal-btn').addEventListener('click', () => {
      closeModal(modalId);
    });
  } else {
    // Update modal title if it already exists
    modal.querySelector('.modal-header h3').textContent = options.isReply ? 'Reply to Message' : 'New Message';
    
    // Update form fields
    document.getElementById('message-recipient').value = options.recipient || '';
    document.getElementById('message-subject').value = options.subject || '';
    document.getElementById('message-content').value = options.content || '';
  }
  
  // Set up form submission
  const sendBtn = document.getElementById('send-message-btn');
  const errorEl = document.getElementById('message-form-error');
  
  sendBtn.onclick = () => {
    // Get form data
    const recipient = document.getElementById('message-recipient').value.trim();
    const subject = document.getElementById('message-subject').value.trim();
    const urgency = document.getElementById('message-urgency').value;
    const content = document.getElementById('message-content').value.trim();
    
    // Validate
    if (!recipient || !subject || !content) {
      errorEl.textContent = 'Please fill out all required fields';
      return;
    }
    
    // Prepare data
    const messageData = {
      recipient,
      subject,
      urgency,
      content,
      is_reply: options.isReply
    };
    
    // Add related fields if it's a reply
    if (options.isReply && options.originalMessage) {
      messageData.reply_to = options.originalMessage.message_id;
      
      if (options.originalMessage.call_id) {
        messageData.call_id = options.originalMessage.call_id;
      }
    }
    
    // Send the message
    api.createMessage(messageData)
      .then(() => {
        closeModal(modalId);
        showNotification('Message sent successfully', 'success');
        loadMessages();
      })
      .catch(error => {
        console.error('Error sending message:', error);
        errorEl.textContent = 'Error sending message. Please try again.';
      });
  };
  
  // Show modal
  openModal(modalId);
}

// Delete message
function deleteMessage(messageId) {
  if (confirm('Are you sure you want to delete this message?')) {
    api.deleteMessage(messageId)
      .then(() => {
        showNotification('Message deleted successfully', 'success');
        loadMessages();
      })
      .catch(error => {
        console.error('Error deleting message:', error);
        showNotification('Error deleting message', 'error');
      });
  }
}

// Function to load messages for the dashboard
function loadRecentMessages() {
  api.getMessages({ page: 1, page_size: 5 })
    .then(data => {
      const messagesContainer = document.getElementById('recent-messages');
      
      if (!data.messages || data.messages.length === 0) {
        messagesContainer.innerHTML = `<p class="placeholder-text">No recent messages</p>`;
        return;
      }
      
      messagesContainer.innerHTML = '';
      
      data.messages.forEach(message => {
        const messageItem = document.createElement('div');
        messageItem.className = `message-item ${message.urgency}`;
        messageItem.innerHTML = `
          <div class="message-header">
            <span class="message-sender">${message.sender || 'System'}</span>
            <span class="message-time">${formatDateTime(message.timestamp)}</span>
          </div>
          <div class="message-preview">
            <span class="urgency-indicator ${message.urgency}">${message.urgency}</span>
            <p class="message-subject">${message.subject || 'No subject'}</p>
          </div>
        `;
        
        // Add click event to view the message
        messageItem.addEventListener('click', () => {
          viewMessage(message.message_id);
        });
        
        messagesContainer.appendChild(messageItem);
      });
    })
    .catch(error => {
      console.error('Error loading recent messages:', error);
      document.getElementById('recent-messages').innerHTML = `
        <p class="placeholder-text">Error loading messages</p>
      `;
    });
}