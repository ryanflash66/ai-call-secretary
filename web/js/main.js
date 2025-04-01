/**
 * Main JavaScript file for the AI Call Secretary web interface.
 * Handles core functionality and initialization.
 */

// Global variables
let AUTH_TOKEN = null;
const API_BASE_URL = 'http://localhost:8080';
let currentPage = 'dashboard';
let systemStatus = {
    components: {},
    uptime: 0
};

// Helper Functions
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function formatTime(dateString) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleTimeString(undefined, options);
}

function formatDateTime(dateString) {
    return `${formatDate(dateString)} ${formatTime(dateString)}`;
}

function formatDuration(seconds) {
    if (!seconds) return '--';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close"><i class="fas fa-times"></i></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Add event listener to close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (document.body.contains(notification)) {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, 5000);
}

// Navigation
function navigateTo(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show the selected page
    const page = document.getElementById(pageId);
    if (page) {
        page.classList.add('active');
        currentPage = pageId;
        
        // Update page title
        document.getElementById('current-page-title').textContent = 
            pageId.charAt(0).toUpperCase() + pageId.slice(1);
        
        // Update active nav link
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageId) {
                link.classList.add('active');
            }
        });
        
        // Handle page-specific initialization
        switch (pageId) {
            case 'dashboard':
                initDashboard();
                break;
            case 'calls':
                initCallsPage();
                break;
            case 'messages':
                initMessagesPage();
                break;
            case 'appointments':
                initAppointmentsPage();
                break;
            case 'settings':
                initSettingsPage();
                break;
        }
        
        // Update URL hash
        window.location.hash = pageId;
    }
}

// Initialize UI elements
function initUI() {
    // Navigation links
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('data-page');
            navigateTo(pageId);
        });
    });
    
    // Settings tabs
    document.querySelectorAll('.settings-nav a').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Hide all settings panels
            document.querySelectorAll('.settings-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            
            // Show the selected panel
            const panelId = link.getAttribute('href').substring(1);
            document.getElementById(panelId).classList.add('active');
            
            // Update active link
            document.querySelectorAll('.settings-nav a').forEach(navLink => {
                navLink.classList.remove('active');
            });
            link.classList.add('active');
        });
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Modal close buttons
    document.querySelectorAll('.close-btn, .close-modal-btn').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            closeModal(modal.id);
        });
    });
    
    // Notification button
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            // Clear notification badge
            const badge = document.querySelector('.notification-badge');
            if (badge) {
                badge.textContent = '0';
                badge.style.display = 'none';
            }
            
            // Show notifications panel (to be implemented)
            alert('Notifications feature coming soon!');
        });
    }
    
    // Handle hash in URL
    if (window.location.hash) {
        const pageId = window.location.hash.substring(1);
        navigateTo(pageId);
    } else {
        navigateTo('dashboard');
    }
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// System status check
function checkSystemStatus() {
    if (!isAuthenticated()) return;
    
    fetch(`${API_BASE_URL}/status`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${AUTH_TOKEN}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch system status');
        }
        return response.json();
    })
    .then(data => {
        systemStatus = data;
        updateSystemStatusUI();
    })
    .catch(error => {
        console.error('Error checking system status:', error);
    });
}

function updateSystemStatusUI() {
    // Update status indicators
    const statusContainer = document.getElementById('system-status');
    if (!statusContainer) return;
    
    // Update component statuses
    Object.entries(systemStatus.components).forEach(([component, status]) => {
        const statusItem = statusContainer.querySelector(`.status-item:contains('${component.charAt(0).toUpperCase() + component.slice(1)}:')`);
        if (statusItem) {
            const statusIndicator = statusItem.querySelector('.status-indicator');
            const statusValue = statusItem.querySelector('.status-value');
            
            statusIndicator.className = `status-indicator ${status === 'operational' ? 'online' : 'offline'}`;
            statusValue.textContent = status === 'operational' ? 'Online' : 'Offline';
        }
    });
    
    // Update uptime
    const uptimeElement = document.getElementById('system-uptime');
    if (uptimeElement) {
        uptimeElement.textContent = formatDuration(systemStatus.uptime);
    }
}

// Initialize the application
function initApp() {
    // Check if user is logged in
    if (isAuthenticated()) {
        initUI();
        checkSystemStatus();
        
        // Initialize WebSocket connection if available
        if (typeof initWebSocket === 'function') {
            initWebSocket();
        }
        
        // Set up periodic status check
        setInterval(checkSystemStatus, 60000); // Every 60 seconds
    } else {
        // Show login modal
        openModal('login-modal');
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to get stored token
    AUTH_TOKEN = localStorage.getItem('auth_token');
    
    initApp();
});

// Authentication check
function isAuthenticated() {
    return !!AUTH_TOKEN;
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