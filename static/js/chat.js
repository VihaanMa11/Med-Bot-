// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const clearChatButton = document.getElementById('clearChat');

// Chat state
let isDiagnosticMode = false;
let sessionId = generateSessionId();
let currentOptions = [];

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    chatForm.addEventListener('submit', handleChatSubmit);
    clearChatButton.addEventListener('click', clearChat);
    
    // Add diagnostic button to the interface
    addDiagnosticButton();
    
    // Load diseases list for autocomplete
    loadDiseasesList();
    
    // Auto-scroll chat to bottom on load
    scrollToBottom();
});

// Generate a unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Add diagnostic button to the interface
function addDiagnosticButton() {
    // Create a diagnostic button
    const diagButton = document.createElement('button');
    diagButton.id = 'startDiagnostic';
    diagButton.className = 'btn btn-warning mt-3 mb-2';
    diagButton.innerHTML = '<i class="fas fa-stethoscope me-2"></i>Start Symptom Checker';
    diagButton.onclick = startDiagnostic;
    
    // Find the welcome message and append the button after it
    const welcomeMsg = chatContainer.querySelector('.bot-message');
    if (welcomeMsg) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'text-center w-100';
        buttonContainer.appendChild(diagButton);
        
        welcomeMsg.insertAdjacentElement('afterend', buttonContainer);
    }
}

// Load diseases list from server
function loadDiseasesList() {
    fetch('/api/diseases')
        .then(response => response.json())
        .then(data => {
            console.log('Loaded diseases list:', data.diseases.length);
            // Here we could implement autocomplete functionality
        })
        .catch(error => {
            console.error('Error loading diseases:', error);
        });
}

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
function addMessage(message, sender, options = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    if (sender === 'user' && options) {
        // For options selected by the user in diagnostic mode
        messageDiv.className += ' diagnostic-response';
    }
    
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
    
    // If options are provided, add them as interactive buttons
    if (options && sender === 'bot') {
        addOptionButtons(options);
    }
    
    // Clear any existing typing indicators
    removeTypingIndicator();
    
    // Scroll to bottom of chat
    scrollToBottom();
}

// Add option buttons for diagnostic mode
function addOptionButtons(options) {
    // Save current options in the global state
    currentOptions = options;
    
    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'diagnostic-options';
    
    // Check if it's a multi-select or single-select
    if (Array.isArray(options) && options.length > 0 && typeof options[0] === 'object' && options[0].symptom) {
        // Multi-select symptom options
        const form = document.createElement('form');
        form.className = 'diagnostic-symptoms-form';
        
        options.forEach(option => {
            const checkboxDiv = document.createElement('div');
            checkboxDiv.className = 'form-check';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input';
            checkbox.id = `symptom-${option.symptom}`;
            checkbox.value = option.symptom;
            
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = `symptom-${option.symptom}`;
            label.textContent = option.display;
            
            checkboxDiv.appendChild(checkbox);
            checkboxDiv.appendChild(label);
            form.appendChild(checkboxDiv);
        });
        
        // Add submit button
        const submitBtn = document.createElement('button');
        submitBtn.type = 'button';
        submitBtn.className = 'btn btn-primary mt-3';
        submitBtn.textContent = 'Submit Symptoms';
        submitBtn.onclick = submitSymptoms;
        
        form.appendChild(submitBtn);
        optionsDiv.appendChild(form);
    } else {
        // Regular options (yes/no or simple buttons)
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary option-button me-2 mb-2';
            button.textContent = option;
            button.onclick = () => selectOption(option);
            optionsDiv.appendChild(button);
        });
    }
    
    chatContainer.appendChild(optionsDiv);
    scrollToBottom();
}

// Submit selected symptoms
function submitSymptoms() {
    const selectedSymptoms = [];
    const checkboxes = document.querySelectorAll('.diagnostic-symptoms-form input[type="checkbox"]:checked');
    
    checkboxes.forEach(checkbox => {
        selectedSymptoms.push(checkbox.value);
    });
    
    // Create a readable list of selected symptoms
    const readableSymptoms = Array.from(checkboxes).map(checkbox => checkbox.nextElementSibling.textContent);
    let message = "Selected symptoms: ";
    if (readableSymptoms.length > 0) {
        message += readableSymptoms.join(", ");
    } else {
        message = "No symptoms selected";
    }
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Remove the options form
    const optionsForm = document.querySelector('.diagnostic-symptoms-form');
    if (optionsForm) {
        optionsForm.parentElement.remove();
    }
    
    // Show typing indicator
    showTypingIndicator();
    
    // Convert selectedSymptoms array to JSON string
    const symptomsJSON = JSON.stringify(selectedSymptoms);
    console.log("Sending symptoms: ", symptomsJSON);
    
    // Send the selected symptoms to the server
    sendDiagnosticResponse(symptomsJSON);
}

// Select an option in diagnostic mode
function selectOption(option) {
    // Add user message to chat
    addMessage(option, 'user');
    
    // Remove the options buttons
    const optionsDiv = document.querySelector('.diagnostic-options');
    if (optionsDiv) {
        optionsDiv.remove();
    }
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send the selected option to the server
    sendDiagnosticResponse(option);
}

// Start the diagnostic process
function startDiagnostic() {
    // Set diagnostic mode
    isDiagnosticMode = true;
    
    // Add message to chat
    addMessage("Starting Symptom Checker...", 'user');
    
    // Show typing indicator
    showTypingIndicator();
    
    // Make API request to start diagnostic
    fetch('/api/start-diagnostic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Process the diagnostic response
        processDiagnosticResponse(data);
    })
    .catch(error => {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error starting the symptom checker. Please try again.', 'bot');
        isDiagnosticMode = false;
    });
}

// Send a diagnostic response to the server
function sendDiagnosticResponse(response) {
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: response,
            session_id: sessionId,
            is_diagnostic: true
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Process the diagnostic response
        processDiagnosticResponse(data);
    })
    .catch(error => {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error in the symptom checker. Let\'s start over.', 'bot');
        isDiagnosticMode = false;
    });
}

// Process a diagnostic response from the server
function processDiagnosticResponse(data) {
    // Remove typing indicator
    removeTypingIndicator();
    
    // Check if we're still in diagnostic mode
    isDiagnosticMode = data.is_diagnostic === true;
    
    // Add bot message to chat
    let options = null;
    
    // For multi-select options (symptoms list)
    if (data.response_type === 'multi_select' && data.multi_options) {
        options = data.multi_options;
    } else if (data.options) {
        options = data.options;
    }
    
    // Add the message
    setTimeout(() => {
        addMessage(data.response, 'bot', options);
        
        // If diagnostic mode ended, cleanup
        if (!isDiagnosticMode) {
            sessionId = generateSessionId(); // Generate a new session ID for next time
        }
    }, 800);
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
    // Check if it's a specific diagnostic command
    if (message.toLowerCase() === 'start symptom checker' || message.toLowerCase() === 'start diagnostic') {
        startDiagnostic();
        return;
    }
    
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
            session_id: sessionId,
            is_diagnostic: isDiagnosticMode
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Check if this is a diagnostic response
        if (data.is_diagnostic) {
            processDiagnosticResponse(data);
        } else {
            // Regular chat response
            setTimeout(() => {
                addMessage(data.response, 'bot');
            }, 800);
        }
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
    // Reset the chat state
    isDiagnosticMode = false;
    sessionId = generateSessionId();
    
    // Keep only the first welcome message
    const welcomeMessage = chatContainer.querySelector('.message');
    chatContainer.innerHTML = '';
    if (welcomeMessage) {
        chatContainer.appendChild(welcomeMessage);
        
        // Re-add the diagnostic button
        addDiagnosticButton();
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
