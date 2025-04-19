import os
import logging
from flask import Flask, render_template, request, jsonify
from nlp_processor import process_query
from health_data import initialize_health_data

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_health_secret_key")

# Initialize health data
health_knowledge_base = initialize_health_data()

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
        
        if not user_query.strip():
            return jsonify({'response': 'Please enter a valid health-related question.'})
        
        # Process the query using NLP
        response = process_query(user_query, health_knowledge_base)
        
        return jsonify({'response': response})
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({'response': 'Sorry, I encountered an error processing your question. Please try again.'})

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'response': 'Internal server error occurred. Please try again later.'}), 500
