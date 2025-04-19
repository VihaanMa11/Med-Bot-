import logging
from disease_predictor import DiseasePredictor

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DiagnosticChat:
    def __init__(self):
        """Initialize the diagnostic chat session."""
        self.predictor = DiseasePredictor()
        self.current_state = "start"
        self.current_category_index = 0
        self.categories = list(self.predictor.get_symptom_categories().items())
        self.selected_symptoms = []
        self.last_category = ""
        self.last_question = ""
        
    def get_next_prompt(self, user_response=None):
        """
        Process user response and get the next prompt in the diagnostic flow.
        
        Args:
            user_response (str): User's response to the previous prompt
            
        Returns:
            dict: Contains prompt message, options (if any), and response type
        """
        # Process the user's previous response if provided
        if user_response is not None:
            self._process_response(user_response)
        
        # Generate the next prompt based on current state
        if self.current_state == "start":
            # Initial message to begin the symptom collection process
            self.current_state = "category_question"
            return {
                "message": "I'll ask you about symptoms in different categories to help identify possible health conditions. Please answer Yes or No to each category.",
                "response_type": "acknowledge",
                "options": ["Continue"]
            }
            
        elif self.current_state == "category_question":
            # Ask about a symptom category
            if self.current_category_index < len(self.categories):
                category, symptoms = self.categories[self.current_category_index]
                self.last_category = category
                self.last_question = f"Do you have any {category.lower()} issues?"
                
                return {
                    "message": self.last_question,
                    "response_type": "yes_no",
                    "options": ["Yes", "No"],
                    "category": category
                }
            else:
                # Finished all categories, move to prediction
                self.current_state = "prediction"
                return self.get_next_prompt()
                
        elif self.current_state == "symptoms_selection":
            # Ask which specific symptoms they have in the current category
            category, symptoms = self.categories[self.current_category_index - 1]
            
            # Convert symptoms to more readable format
            readable_symptoms = []
            for symptom in symptoms:
                readable = symptom.replace('_', ' ').strip()
                readable = readable.capitalize()
                readable_symptoms.append({"symptom": symptom, "display": readable})
                
            return {
                "message": f"Please select all {category.lower()} symptoms you're experiencing:",
                "response_type": "multi_select",
                "options": readable_symptoms
            }
            
        elif self.current_state == "prediction":
            # Check if we have enough symptoms for prediction
            if len(self.selected_symptoms) < 1:
                self.current_state = "end"
                return {
                    "message": "You haven't selected any symptoms. I need at least one symptom to suggest possible conditions.",
                    "response_type": "acknowledge",
                    "options": ["Start Over"]
                }
            
            # Make disease prediction
            prediction_results = self.predictor.predict_disease(self.selected_symptoms)
            
            if not prediction_results:
                self.current_state = "end"
                return {
                    "message": "I couldn't determine any conditions based on the symptoms provided. Please consult a healthcare professional for a proper diagnosis.",
                    "response_type": "acknowledge",
                    "options": ["Start Over"]
                }
            
            # Format the prediction results
            prediction_message = self._format_prediction_results(prediction_results)
            self.current_state = "end"
            
            return {
                "message": prediction_message,
                "response_type": "acknowledge",
                "options": ["Start Over"],
                "predictions": prediction_results
            }
            
        elif self.current_state == "end":
            # Reset the diagnostic session
            self.current_state = "start"
            self.current_category_index = 0
            self.selected_symptoms = []
            return self.get_next_prompt()
            
        # Default response if state is undefined
        return {
            "message": "I'm not sure how to proceed. Let's start over.",
            "response_type": "acknowledge",
            "options": ["Start Over"]
        }
    
    def _process_response(self, response):
        """Process the user's response based on current state."""
        if self.current_state == "category_question":
            # Convert string responses to lowercase for comparison
            if isinstance(response, str) and response.lower() in ["yes", "y"]:
                # Move to symptom selection for this category
                self.current_state = "symptoms_selection"
            else:
                # Skip to next category
                self.current_category_index += 1
                self.current_state = "category_question"
                
        elif self.current_state == "symptoms_selection":
            # Add selected symptoms to the list
            if isinstance(response, list):
                # It's already a list of symptoms
                self.selected_symptoms.extend(response)
            elif isinstance(response, str):
                try:
                    # It might be a JSON string representation of a list
                    import json
                    symptoms_list = json.loads(response)
                    if isinstance(symptoms_list, list):
                        self.selected_symptoms.extend(symptoms_list)
                    else:
                        # Just a single symptom as string
                        self.selected_symptoms.append(response.strip())
                except:
                    # Not JSON, treat as a single symptom
                    if response.strip():
                        self.selected_symptoms.append(response.strip())
            
            # Debug log
            logger.debug(f"Added symptoms: {response}")
            logger.debug(f"Total selected symptoms: {self.selected_symptoms}")
                
            # Move to next category
            self.current_category_index += 1
            self.current_state = "category_question"
            
        elif self.current_state in ["prediction", "end"]:
            # Reset for a new session
            self.current_state = "start"
            self.current_category_index = 0
            self.selected_symptoms = []
    
    def _format_prediction_results(self, predictions):
        """Format prediction results into a readable message."""
        message = "<h3>Based on your symptoms, here are the most likely conditions:</h3><ul>"
        
        for i, pred in enumerate(predictions):
            disease = pred["disease"]
            description = pred["description"]
            precautions = pred["precautions"]
            
            # Limit description length
            if len(description) > 150:
                description = description[:150] + "..."
                
            message += f"<li><strong>{disease}</strong> - {description}</li>"
        
        message += "</ul>"
        
        # Add precautions section if available
        if predictions and predictions[0]["precautions"]:
            message += "<h4>Recommended Precautions:</h4><ul>"
            for precaution in predictions[0]["precautions"]:
                message += f"<li>{precaution}</li>"
            message += "</ul>"
            
        message += "<p><em>Note: This information is for educational purposes only. Please consult a healthcare professional for proper diagnosis and treatment.</em></p>"
        
        return message
        
    def start_diagnostic(self):
        """Start a new diagnostic session."""
        self.current_state = "start"
        self.current_category_index = 0
        self.selected_symptoms = []
        return self.get_next_prompt()
        
    def get_all_symptoms(self):
        """Get all available symptoms."""
        symptoms = []
        for category, category_symptoms in self.predictor.get_symptom_categories().items():
            for symptom in category_symptoms:
                readable = symptom.replace('_', ' ').strip()
                readable = readable.capitalize()
                symptoms.append({"symptom": symptom, "display": readable, "category": category})
        
        return symptoms