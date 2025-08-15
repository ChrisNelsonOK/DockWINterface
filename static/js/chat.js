// DockWINterface AI Chat JavaScript

// Chat state
let chatHistory = [];
let isTyping = false;
let contextMode = 'conversational';
let messageCount = 0;
let autoRefreshInterval = null;

// Initialize chat
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupChatForm();
    setupContextSettings();
    loadChatHistory();
    updateAIStatus();
});

function initializeChat() {
    // Auto-resize message input
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('input', autoResizeTextarea);
        messageInput.addEventListener('keydown', handleInputKeydown);
    }
    
    // Load AI configuration
    loadAIConfiguration();
    
    // Setup periodic status checks
    setInterval(updateAIStatus, 30000);
}

function setupChatForm() {
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }
}

function setupContextSettings() {
    // Load saved settings
    const savedProvider = localStorage.getItem('ai_provider');
    const savedContextMode = localStorage.getItem('context_mode');
    
    if (savedProvider) {
        const providerSelect = document.getElementById('aiProvider');
        if (providerSelect) {
            providerSelect.value = savedProvider;
        }
    }
    
    if (savedContextMode) {
        const contextSelect = document.getElementById('contextMode');
        if (contextSelect) {
            contextSelect.value = savedContextMode;
            contextMode = savedContextMode;
        }
    }
    
    // Setup event listeners
    const contextSelect = document.getElementById('contextMode');
    if (contextSelect) {
        contextSelect.addEventListener('change', function() {
            contextMode = this.value;
            localStorage.setItem('context_mode', contextMode);
        });
    }
}

function loadAIConfiguration() {
    const apiKey = localStorage.getItem('openai_api_key');
    const apiKeyInput = document.getElementById('apiKeyInput');
    
    if (apiKey && apiKeyInput) {
        apiKeyInput.value = apiKey;
    }
}

function saveAIConfig() {
    const provider = document.getElementById('aiProvider').value;
    const apiKey = document.getElementById('apiKeyInput').value;
    const contextMode = document.getElementById('contextMode').value;
    
    if (apiKey) {
        localStorage.setItem('openai_api_key', apiKey);
    }
    
    localStorage.setItem('ai_provider', provider);
    localStorage.setItem('context_mode', contextMode);
    
    showNotification('AI configuration saved', 'success');
    updateAIStatus();
}

function updateAIStatus() {
    const statusIndicator = document.getElementById('aiStatus');
    const statusText = document.getElementById('aiStatusText');
    const messageCountEl = document.getElementById('messageCount');
    
    const hasApiKey = localStorage.getItem('openai_api_key');
    
    if (statusIndicator && statusText) {
        if (hasApiKey) {
            statusIndicator.className = 'ai-status-indicator ai-status-connected';
            statusText.textContent = 'AI Assistant Ready';
        } else {
            statusIndicator.className = 'ai-status-indicator ai-status-disconnected';
            statusText.textContent = 'API Key Required';
        }
    }
    
    if (messageCountEl) {
        messageCountEl.textContent = messageCount;
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    
    if (!messageInput || !messageInput.value.trim()) {
        return;
    }
    
    const message = messageInput.value.trim();
    messageInput.value = '';
    resetTextareaHeight(messageInput);
    
    // Check if API key is configured
    const apiKey = localStorage.getItem('openai_api_key');
    if (!apiKey) {
        showNotification('Please configure your OpenAI API key first', 'warning');
        return;
    }
    
    // Disable input while processing
    messageInput.disabled = true;
    sendButton.disabled = true;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Collect context if enabled
        const context = collectContext();
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: context
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI response to chat
            addMessageToChat('ai', result.response);
            
            // Update statistics
            messageCount++;
            incrementStat('aiQueries');
            updateAIStatus();
            
            // Save to history
            saveChatHistory();
            
            // Update recent topics
            updateRecentTopics(message);
            
        } else {
            throw new Error(result.error || 'AI request failed');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        addMessageToChat('ai', `Sorry, I encountered an error: ${error.message}. Please check your API key configuration and try again.`);
        showNotification('Failed to send message: ' + error.message, 'error');
    } finally {
        // Re-enable input
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

function addMessageToChat(sender, content) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString();
    const authorName = sender === 'user' ? 'You' : 'DockWINterface AI';
    const avatarIcon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">${authorName}</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-text">${formatMessageContent(content)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to chat history
    chatHistory.push({
        sender: sender,
        content: content,
        timestamp: new Date().toISOString()
    });
    
    // Animate message appearance
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
}

function formatMessageContent(content) {
    // Convert markdown-style formatting to HTML
    content = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    // Convert lists
    content = content.replace(/^\s*[-*+]\s+(.+)$/gm, '<li>$1</li>');
    content = content.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    return content;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message ai-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-author">DockWINterface AI</span>
                <span class="message-time">typing...</span>
            </div>
            <div class="message-text">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    isTyping = true;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isTyping = false;
}

function collectContext() {
    const context = {};
    
    // Include system information if enabled
    if (document.getElementById('includeSystemInfo')?.checked) {
        context.systemInfo = {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            timestamp: new Date().toISOString()
        };
    }
    
    // Include current configuration if enabled
    if (document.getElementById('includeCurrentConfig')?.checked) {
        const savedConfig = localStorage.getItem('wizardFormData');
        if (savedConfig) {
            try {
                context.currentConfig = JSON.parse(savedConfig);
            } catch (e) {
                console.error('Failed to parse saved configuration:', e);
            }
        }
    }
    
    // Include error logs if enabled
    if (document.getElementById('includeErrorLogs')?.checked) {
        const recentErrors = getRecentErrors();
        if (recentErrors.length > 0) {
            context.recentErrors = recentErrors;
        }
    }
    
    // Include context mode
    context.mode = contextMode;
    
    return context;
}

function getRecentErrors() {
    // Get recent error messages from console or logs
    // This is a simplified implementation
    return [];
}

function askQuickQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.value = question;
        messageInput.focus();
        autoResizeTextarea({ target: messageInput });
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            // Keep the welcome message
            const welcomeMessage = chatMessages.querySelector('.ai-message');
            chatMessages.innerHTML = '';
            if (welcomeMessage) {
                chatMessages.appendChild(welcomeMessage);
            }
        }
        
        chatHistory = [];
        messageCount = 0;
        updateAIStatus();
        localStorage.removeItem('chatHistory');
        showNotification('Chat cleared', 'success');
    }
}

function exportChat() {
    if (chatHistory.length === 0) {
        showNotification('No chat history to export', 'warning');
        return;
    }
    
    const exportData = {
        timestamp: new Date().toISOString(),
        messageCount: chatHistory.length,
        messages: chatHistory
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dokwinterface-chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Chat history exported', 'success');
}

function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    } catch (e) {
        console.error('Failed to save chat history:', e);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            chatHistory = JSON.parse(saved);
            messageCount = chatHistory.length;
            
            // Restore chat messages (limit to last 10 for performance)
            const recentHistory = chatHistory.slice(-10);
            const chatMessages = document.getElementById('chatMessages');
            
            // Remove welcome message temporarily
            const welcomeMessage = chatMessages.querySelector('.ai-message');
            
            recentHistory.forEach(msg => {
                if (msg.sender !== 'ai' || !welcomeMessage) {
                    addMessageToChat(msg.sender, msg.content);
                }
            });
        }
    } catch (e) {
        console.error('Failed to load chat history:', e);
    }
}

function updateRecentTopics(message) {
    const recentTopicsContainer = document.getElementById('recentTopics');
    if (!recentTopicsContainer) return;
    
    let topics = JSON.parse(localStorage.getItem('recentTopics') || '[]');
    
    // Add new topic (first 50 characters)
    const topic = message.substring(0, 50) + (message.length > 50 ? '...' : '');
    topics.unshift({
        text: topic,
        timestamp: new Date().toISOString()
    });
    
    // Keep only last 5 topics
    topics = topics.slice(0, 5);
    
    localStorage.setItem('recentTopics', JSON.stringify(topics));
    
    // Update UI
    if (topics.length > 0) {
        recentTopicsContainer.innerHTML = topics.map(topic => `
            <div class="recent-topic-item" onclick="askQuickQuestion('${topic.text}')">
                <small>${topic.text}</small>
                <div><small class="text-muted">${new Date(topic.timestamp).toLocaleDateString()}</small></div>
            </div>
        `).join('');
    }
}

function toggleApiKeyVisibility() {
    const input = document.getElementById('apiKeyInput');
    const icon = document.getElementById('apiKeyToggleIcon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function handleInputKeydown(event) {
    // Send message on Enter (but not Shift+Enter)
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResizeTextarea(event) {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function resetTextareaHeight(textarea) {
    textarea.style.height = 'auto';
}

// Add CSS for typing indicator
const typingStyles = `
.typing-indicator .typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: currentColor;
    opacity: 0.4;
    animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        opacity: 0.4;
    }
    30% {
        opacity: 1;
    }
}
`;

// Inject typing styles
const styleSheet = document.createElement('style');
styleSheet.textContent = typingStyles;
document.head.appendChild(styleSheet);

// Export functions to global scope
window.sendMessage = sendMessage;
window.askQuickQuestion = askQuickQuestion;
window.clearChat = clearChat;
window.exportChat = exportChat;
window.saveAIConfig = saveAIConfig;
window.toggleApiKeyVisibility = toggleApiKeyVisibility;
