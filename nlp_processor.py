import nltk
import string
import logging
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download required NLTK packages
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    logger.info("NLTK packages downloaded successfully")
except Exception as e:
    logger.error(f"Error downloading NLTK packages: {str(e)}")

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """
    Preprocess text by tokenizing, removing punctuation, 
    converting to lowercase, removing stop words, and lemmatizing
    """
    try:
        # Lowercase the text
        text = text.lower()
        
        # Remove punctuation
        text = ''.join([char for char in text if char not in string.punctuation])
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stop words and lemmatize
        processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
        
        return processed_tokens
    except Exception as e:
        logger.error(f"Error in text preprocessing: {str(e)}")
        # Fallback processing if tokenization fails
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        tokens = text.split()
        processed_tokens = [token for token in tokens if token not in stop_words]
        return processed_tokens

def extract_keywords(tokens):
    """Extract the most important keywords from preprocessed tokens"""
    # Count word frequencies
    word_freq = Counter(tokens)
    
    # Get the most common words (keywords)
    keywords = [word for word, count in word_freq.most_common(5)]
    
    return keywords

def calculate_similarity(query_keywords, topic_keywords):
    """Calculate similarity between query keywords and topic keywords"""
    # Find intersection of keywords
    common_keywords = set(query_keywords).intersection(set(topic_keywords))
    
    # Calculate Jaccard similarity
    if not query_keywords or not topic_keywords:
        return 0
    
    similarity = len(common_keywords) / len(set(query_keywords).union(set(topic_keywords)))
    return similarity

def find_best_match(query_keywords, health_knowledge_base):
    """Find the best matching health topic for the query"""
    best_match = None
    highest_similarity = 0
    
    for disease, data in health_knowledge_base.items():
        # Calculate similarity between query and disease
        disease_keywords = data.get('keywords', [])
        similarity = calculate_similarity(query_keywords, disease_keywords)
        
        # Update best match if this disease has higher similarity
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = disease
    
    # Return the best match if similarity is above threshold
    threshold = 0.1  # Adjust threshold based on testing
    if highest_similarity >= threshold:
        return best_match, highest_similarity
    
    return None, 0

def format_disease_response(disease, disease_data):
    """Format the response data for a specific disease."""
    description = disease_data.get('description', '')
    symptoms = disease_data.get('symptoms', [])
    precautions = disease_data.get('precautions', [])
    diets = disease_data.get('diets', [])
    medications = disease_data.get('medications', [])
    
    # Create HTML response
    response = f"""<h3>{disease}</h3>
<p><strong>Description:</strong> {description}</p>"""
    
    if symptoms:
        response += "<p><strong>Common Symptoms:</strong></p><ul>"
        for symptom in symptoms[:5]:  # Show top 5 symptoms
            # Clean up symptom text (replace underscores with spaces, etc.)
            clean_symptom = symptom.replace('_', ' ').strip()
            response += f"<li>{clean_symptom}</li>"
        response += "</ul>"
    
    if precautions:
        response += "<p><strong>Precautions:</strong></p><ul>"
        for precaution in precautions:
            response += f"<li>{precaution}</li>"
        response += "</ul>"
    
    if diets:
        response += "<p><strong>Recommended Diet:</strong></p><ul>"
        for diet in diets[:5]:  # Show top 5 diet recommendations
            response += f"<li>{diet}</li>"
        response += "</ul>"
    
    if medications:
        response += "<p><strong>Common Medications:</strong></p><ul>"
        for medication in medications[:5]:  # Show top 5 medications
            response += f"<li>{medication}</li>"
        response += "</ul>"
    
    response += "<p><em>Note: This information is for educational purposes only. Always consult with a healthcare professional for medical advice.</em></p>"
    
    return response

def process_query(query, health_knowledge_base):
    """Process the user query and return a relevant response"""
    try:
        # Preprocess the query
        processed_query = preprocess_text(query)
        
        # Extract keywords from the query
        query_keywords = extract_keywords(processed_query)
        
        # Find the best matching health topic
        best_match, similarity = find_best_match(query_keywords, health_knowledge_base)
        
        if best_match:
            # Get disease data from the knowledge base
            disease_data = health_knowledge_base[best_match]
            logger.debug(f"Query matched with disease '{best_match}' (similarity: {similarity:.2f})")
            
            # Format the response
            response = format_disease_response(best_match, disease_data)
            return response
        else:
            # No good match found
            return """<p>I'm sorry, I don't have specific information about that health topic. Please try asking about one of the following diseases:</p>
<ul>
    <li>Fungal infection</li>
    <li>Allergy</li>
    <li>GERD (Gastroesophageal Reflux Disease)</li>
    <li>Diabetes</li>
    <li>Bronchial Asthma</li>
    <li>Hypertension</li>
    <li>Migraine</li>
    <li>Hepatitis</li>
    <li>Arthritis</li>
</ul>"""
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return "I'm sorry, I had trouble understanding your question. Please try rephrasing it."
