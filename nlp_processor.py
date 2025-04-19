import nltk
import string
import logging
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
    # Lowercase the text
    text = text.lower()
    
    # Remove punctuation
    text = ''.join([char for char in text if char not in string.punctuation])
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stop words and lemmatize
    processed_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
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
    
    for topic, data in health_knowledge_base.items():
        # Calculate similarity between query and topic
        topic_keywords = data.get('keywords', [])
        similarity = calculate_similarity(query_keywords, topic_keywords)
        
        # Update best match if this topic has higher similarity
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = topic
    
    # Return the best match if similarity is above threshold
    threshold = 0.1  # Adjust threshold based on testing
    if highest_similarity >= threshold:
        return best_match, highest_similarity
    
    return None, 0

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
            # Get response from the knowledge base
            response = health_knowledge_base[best_match]['information']
            logger.debug(f"Query matched with topic '{best_match}' (similarity: {similarity:.2f})")
            return response
        else:
            # No good match found
            return "I'm sorry, I don't have specific information about that health topic. Please try asking about nutrition, exercise, mental health, or common illnesses."
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return "I'm sorry, I had trouble understanding your question. Please try rephrasing it."
