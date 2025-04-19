import os
import logging
import json
from flask import Flask, render_template, request, jsonify, session
from nlp_processor import process_query
from data_processor import initialize_health_data
from diagnostic_chat import DiagnosticChat

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_health_secret_key")

# Initialize health data
health_knowledge_base = initialize_health_data()

# Diagnostic sessions storage
diagnostic_sessions = {}

@app.route('/')
def index():
    """Render the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process the user query and return a response"""
    try:
        data = request.json
        user_query = data.get('message', '')
        session_id = data.get('session_id', 'default')
        is_diagnostic = data.get('is_diagnostic', False)
        
        # Handle diagnostic chat if active
        if is_diagnostic:
            return handle_diagnostic_chat(user_query, session_id)
        
        # For regular chat, ensure we have a non-empty string
        if not isinstance(user_query, str) or not user_query.strip():
            return jsonify({'response': 'Please enter a valid health-related question.'})
        
        # Check for special commands
        if user_query.lower() == "start diagnostic":
            # Initialize a diagnostic session
            diagnostic_sessions[session_id] = DiagnosticChat()
            next_prompt = diagnostic_sessions[session_id].get_next_prompt()
            
            return jsonify({
                'response': next_prompt['message'],
                'is_diagnostic': True,
                'options': next_prompt.get('options', []),
                'response_type': next_prompt.get('response_type', 'text')
            })
        
        # Process regular query using NLP
        response = process_query(user_query, health_knowledge_base)
        
        return jsonify({'response': response})
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your question. Please try again.'})

def handle_diagnostic_chat(user_response, session_id):
    """Handle diagnostic chat interactions"""
    try:
        # Make sure the session exists
        if session_id not in diagnostic_sessions:
            diagnostic_sessions[session_id] = DiagnosticChat()
        
        # Get the diagnostic chat instance
        diagnostic = diagnostic_sessions[session_id]
        
        # Process the user's response
        next_prompt = diagnostic.get_next_prompt(user_response)
        
        # Prepare the response
        response = {
            'response': next_prompt['message'],
            'is_diagnostic': True,
            'options': next_prompt.get('options', []),
            'response_type': next_prompt.get('response_type', 'text')
        }
        
        # If multi-select, include the symptoms
        if next_prompt.get('response_type') == 'multi_select':
            response['multi_options'] = next_prompt.get('options', [])
        
        # If predictions are available, include them
        if 'predictions' in next_prompt:
            response['predictions'] = next_prompt['predictions']
            
        # If it's the end state, clean up the session
        if diagnostic.current_state == "end":
            del diagnostic_sessions[session_id]
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in diagnostic chat: {str(e)}")
        return jsonify({
            'response': 'Sorry, I encountered an error in the diagnostic process. Let\'s start over.',
            'is_diagnostic': False
        })

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """Return a list of all diseases in the knowledge base"""
    try:
        diseases = sorted(list(health_knowledge_base.keys()))
        return jsonify({'diseases': diseases})
    except Exception as e:
        logger.error(f"Error retrieving diseases: {str(e)}")
        return jsonify({'diseases': []}), 500

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Return a list of all symptoms for the diagnostic tool"""
    try:
        diagnostic = DiagnosticChat()
        symptoms = diagnostic.get_all_symptoms()
        return jsonify({'symptoms': symptoms})
    except Exception as e:
        logger.error(f"Error retrieving symptoms: {str(e)}")
        return jsonify({'symptoms': []}), 500

@app.route('/api/start-diagnostic', methods=['POST'])
def start_diagnostic():
    """Start a new diagnostic session"""
    try:
        session_id = request.json.get('session_id', 'default')
        diagnostic_sessions[session_id] = DiagnosticChat()
        next_prompt = diagnostic_sessions[session_id].start_diagnostic()
        
        return jsonify({
            'response': next_prompt['message'],
            'is_diagnostic': True,
            'options': next_prompt.get('options', []),
            'response_type': next_prompt.get('response_type', 'text')
        })
    except Exception as e:
        logger.error(f"Error starting diagnostic: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error starting the diagnostic. Please try again.'}), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'response': 'Internal server error occurred. Please try again later.'}), 500
