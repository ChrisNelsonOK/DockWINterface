// DockWINterface Main JavaScript
// Common functionality and utilities

// Global variables
let notificationContainer = null;

// Initialize main functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeNotifications();
    loadStoredSettings();
    initializeGlobalEventListeners();
});

// Notification System
function initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notificationContainer')) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notificationContainer';
        notificationContainer.className = 'position-fixed top-0 end-0 p-3';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    } else {
        notificationContainer = document.getElementById('notificationContainer');
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const iconMap = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center">
                <i class="${iconMap[type] || iconMap.info} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    notificationContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        delay: duration
    });
    
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// API Key Management
function saveApiKeys() {
    const openaiKey = document.getElementById('openaiKey').value;
    const connectionMethod = document.querySelector('input[name="connectionMethod"]:checked').value;
    
    // Store API keys in localStorage
    if (openaiKey) {
        localStorage.setItem('openai_api_key', openaiKey);
    }
    
    // Store connection settings based on method
    localStorage.setItem('connection_method', connectionMethod);
    
    if (connectionMethod === 'direct') {
        const dockerHost = document.getElementById('dockerHost').value;
        if (dockerHost) {
            localStorage.setItem('docker_host', dockerHost);
        }
    } else if (connectionMethod === 'ssh') {
        const sshHost = document.getElementById('sshHost').value;
        const sshUser = document.getElementById('sshUser').value;
        const sshPort = document.getElementById('sshPort').value;
        const sshAuth = document.querySelector('input[name="sshAuth"]:checked').value;
        
        localStorage.setItem('ssh_host', sshHost);
        localStorage.setItem('ssh_user', sshUser);
        localStorage.setItem('ssh_port', sshPort);
        localStorage.setItem('ssh_auth', sshAuth);
        
        if (sshAuth === 'password') {
            const sshPass = document.getElementById('sshPass').value;
            if (sshPass) {
                localStorage.setItem('ssh_password', btoa(sshPass)); // Basic encoding
            }
        } else {
            const sshKeyPath = document.getElementById('sshKeyPath').value;
            localStorage.setItem('ssh_key_path', sshKeyPath);
        }
    }
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
    modal.hide();
    
    // Show success message
    showNotification('Settings saved successfully', 'success');
}

function loadStoredSettings() {
    const openaiKey = localStorage.getItem('openai_api_key');
    const connectionMethod = localStorage.getItem('connection_method') || 'direct';
    
    if (openaiKey) {
        document.getElementById('openaiKey').value = openaiKey;
    }
    
    // Set connection method
    document.getElementById(connectionMethod === 'ssh' ? 'sshConnection' : 'directConnection').checked = true;
    toggleConnectionSettings(connectionMethod);
    
    if (connectionMethod === 'direct') {
        const dockerHost = localStorage.getItem('docker_host');
        if (dockerHost) {
            document.getElementById('dockerHost').value = dockerHost;
        }
    } else if (connectionMethod === 'ssh') {
        const sshHost = localStorage.getItem('ssh_host');
        const sshUser = localStorage.getItem('ssh_user');
        const sshPort = localStorage.getItem('ssh_port') || '22';
        const sshAuth = localStorage.getItem('ssh_auth') || 'password';
        
        if (sshHost) document.getElementById('sshHost').value = sshHost;
        if (sshUser) document.getElementById('sshUser').value = sshUser;
        document.getElementById('sshPort').value = sshPort;
        
        document.getElementById(sshAuth === 'key' ? 'sshKey' : 'sshPassword').checked = true;
        toggleSSHAuthFields(sshAuth);
        
        if (sshAuth === 'password') {
            const sshPass = localStorage.getItem('ssh_password');
            if (sshPass) {
                document.getElementById('sshPass').value = atob(sshPass);
            }
        } else {
            const sshKeyPath = localStorage.getItem('ssh_key_path');
            if (sshKeyPath) document.getElementById('sshKeyPath').value = sshKeyPath;
        }
    }
}

function toggleConnectionSettings(method) {
    document.getElementById('directSettings').style.display = method === 'direct' ? 'block' : 'none';
    document.getElementById('sshSettings').style.display = method === 'ssh' ? 'block' : 'none';
}

function toggleSSHAuthFields(authType) {
    document.getElementById('sshPasswordField').style.display = authType === 'password' ? 'block' : 'none';
    document.getElementById('sshKeyField').style.display = authType === 'key' ? 'block' : 'none';
}

// Global Event Listeners
function initializeGlobalEventListeners() {
    // Handle settings modal show event
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.addEventListener('show.bs.modal', function() {
            loadStoredSettings();
        });
    }
    
    // Connection method toggle
    document.querySelectorAll('input[name="connectionMethod"]').forEach(radio => {
        radio.addEventListener('change', function() {
            toggleConnectionSettings(this.value);
        });
    });
    
    // SSH auth method toggle
    document.querySelectorAll('input[name="sshAuth"]').forEach(radio => {
        radio.addEventListener('change', function() {
            toggleSSHAuthFields(this.value);
        });
    });
    
    // Handle logs modal show event
    const logsModal = document.getElementById('logsModal');
    if (logsModal) {
        logsModal.addEventListener('show.bs.modal', function() {
            loadApplicationLogs();
        });
    }
    
    // Global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// System Status Updates
function updateSystemStatus() {
    // This function is called from dashboard and other pages
    // Check if elements exist before updating
    if (typeof window.updateSystemStatus === 'function') {
        return; // Let page-specific implementation handle it
    }
    
    // Default implementation for status indicators
    const indicators = document.querySelectorAll('.status-indicator');
    indicators.forEach(indicator => {
        if (indicator.id === 'aiStatus') {
            const hasApiKey = localStorage.getItem('openai_api_key');
            indicator.className = `status-indicator ${hasApiKey ? 'status-good' : 'status-warning'}`;
        }
    });
}

// Utility Functions
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        showNotification('Element not found', 'error');
        return;
    }
    
    const text = element.textContent || element.value;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard', 'success', 2000);
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard', 'success', 2000);
    } catch (err) {
        showNotification('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function refreshLogs() {
    loadApplicationLogs();
}

function loadApplicationLogs() {
    const logsContent = document.getElementById('logsContent');
    if (!logsContent) return;
    
    // Production: Show information about accessing real logs
    logsContent.innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="fas fa-file-alt fa-2x mb-3"></i>
            <p class="mb-3">Application logs will be available here when containers are running.</p>
            <div class="text-start">
                <p><strong>View container logs:</strong></p>
                <code class="d-block bg-dark p-2 rounded">docker logs [container-name]</code>
                <p class="mt-3"><strong>Follow real-time logs:</strong></p>
                <code class="d-block bg-dark p-2 rounded">docker logs -f [container-name]</code>
            </div>
        </div>
    `;
}

// Format utilities
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function formatFileSize(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Statistics management
function updateStat(statId, value) {
    const element = document.getElementById(statId);
    if (element) {
        element.textContent = value;
        localStorage.setItem(statId.replace(/([A-Z])/g, '_$1').toLowerCase(), value);
    }
}

function incrementStat(statId) {
    const current = parseInt(localStorage.getItem(statId.replace(/([A-Z])/g, '_$1').toLowerCase()) || '0');
    updateStat(statId, current + 1);
}

// Form validation utilities
function validateRequired(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function clearFormValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const fields = form.querySelectorAll('.is-invalid, .is-valid');
    fields.forEach(field => {
        field.classList.remove('is-invalid', 'is-valid');
    });
}

// Loading states
function setLoading(elementId, isLoading = true) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (isLoading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Network utilities
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        showNotification(`Request failed: ${error.message}`, 'error');
        throw error;
    }
}

// Export functions for use in other modules
window.DockWINterface = {
    showNotification,
    copyToClipboard,
    togglePassword,
    updateStat,
    incrementStat,
    validateRequired,
    clearFormValidation,
    setLoading,
    makeRequest,
    saveApiKeys,
    refreshLogs
};
