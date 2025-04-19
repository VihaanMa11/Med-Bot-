// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const clearChatButton = document.getElementById('clearChat');

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    chatForm.addEventListener('submit', handleChatSubmit);
    clearChatButton.addEventListener('click', clearChat);
    
    // Auto-scroll chat to bottom on load
    scrollToBottom();
});

// Handle chat form submission
function handleChatSubmit(e) {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input field
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to server
    sendMessage(message);
}

// Add a message to the chat container
function addMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // If it's a bot message with HTML content, display it properly
    if (sender === 'bot' && (message.includes('<') && message.includes('>'))) {
        messageContent.innerHTML = message;
    } else {
        const messagePara = document.createElement('p');
        messagePara.textContent = message;
        messageContent.appendChild(messagePara);
    }
    
    messageDiv.appendChild(messageContent);
    chatContainer.appendChild(messageDiv);
    
    // Clear any existing typing indicators
    removeTypingIndicator();
    
    // Scroll to bottom of chat
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message typing-indicator-container';
    typingDiv.id = 'typing-indicator';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    
    // Add three dots for the typing animation
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        typingIndicator.appendChild(dot);
    }
    
    typingDiv.appendChild(typingIndicator);
    chatContainer.appendChild(typingDiv);
    
    // Scroll to bottom of chat
    scrollToBottom();
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Send message to server
function sendMessage(message) {
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Add bot response to chat
        setTimeout(() => {
            addMessage(data.response, 'bot');
        }, 800); // Slight delay to simulate thinking time
    })
    .catch(error => {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error processing your question. Please try again.', 'bot');
    });
}

// Scroll to bottom of chat container
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Clear chat history
function clearChat() {
    // Keep only the first welcome message
    const welcomeMessage = chatContainer.querySelector('.message');
    chatContainer.innerHTML = '';
    if (welcomeMessage) {
        chatContainer.appendChild(welcomeMessage);
    }
}

// Function to handle topic suggestion clicks
function suggestTopic(topic) {
    // Set the input field value
    userInput.value = topic;
    
    // Submit the form
    const submitEvent = new Event('submit', {
        'bubbles': true,
        'cancelable': true
    });
    chatForm.dispatchEvent(submitEvent);
}
